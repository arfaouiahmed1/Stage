from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from io import BytesIO
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score, davies_bouldin_score
from minisom import MiniSom
import gower
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

REQUIRED_COLS = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class", "gender", "nationality", "age"}

# Utility functions
def entropy(series):
    counts = series.value_counts()
    probs = counts / counts.sum()
    return -(probs * np.log2(probs + 1e-9)).sum()

def gender_nationality_entropy(df, labels):
    df_temp = df.copy()
    df_temp['cluster'] = labels
    gender_e = df_temp.groupby('cluster')['gender'].agg(lambda x: entropy(x)).mean()
    nat_e = df_temp.groupby('cluster')['nationality'].agg(lambda x: entropy(x)).mean()
    return gender_e, nat_e

def run_algorithms(X_scaled, df, distance_metric):
    results = []
    kmeans = KMeans(n_clusters=4, random_state=42)
    results.append(("KMeans", kmeans.fit_predict(X_scaled)))

    agg = AgglomerativeClustering(n_clusters=4, metric='euclidean', linkage='ward')
    results.append(("Agglomerative", agg.fit_predict(X_scaled)))

    dbscan = DBSCAN(metric=distance_metric if distance_metric != 'gower' else 'precomputed', eps=0.6, min_samples=5)
    if distance_metric == 'gower':
        dist_mat = gower.gower_matrix(df[list(REQUIRED_COLS - {"first_name", "last_name", "class"})])
        db_labels = dbscan.fit_predict(dist_mat)
    else:
        db_labels = dbscan.fit_predict(X_scaled)
    results.append(("DBSCAN", db_labels))

    spectral = SpectralClustering(n_clusters=4, affinity='nearest_neighbors',n_neighbors=15, random_state=42)
    results.append(("Spectral", spectral.fit_predict(X_scaled)))

    gmm = GaussianMixture(n_components=4, random_state=42)
    results.append(("GMM", gmm.fit_predict(X_scaled)))

    try:
        meanshift = MeanShift()
        ms_labels = meanshift.fit_predict(X_scaled)
        results.append(("MeanShift", ms_labels))
    except:
        pass

    som = MiniSom(6, 6, X_scaled.shape[1], sigma=1.0, learning_rate=0.5)
    som.random_weights_init(X_scaled)
    som.train_random(X_scaled, 100)
    som_labels = np.array([som.winner(x)[0]*6 + som.winner(x)[1] for x in X_scaled])
    results.append(("MiniSom", som_labels))

    return results

def evaluate_algorithms(X_scaled, df, results, features):
    eval_data = []
    for algo_name, labels in results:
        if len(set(labels)) <= 1:
            continue
        try:
            sil = silhouette_score(X_scaled, labels)
        except:
            sil = np.nan
        try:
            dbs = davies_bouldin_score(X_scaled, labels)
        except:
            dbs = np.nan
        ge, ne = gender_nationality_entropy(df, labels)
        eval_data.append((algo_name, sil, dbs, ge, ne))
    return eval_data

def create_initial_groups(df, group_size_min=5, group_size_max=7):
    n_students = len(df)
    n_groups = max(1, n_students // group_size_min)
    groups = [[] for _ in range(n_groups)]
    for i, idx in enumerate(df.index):
        groups[i % n_groups].append(idx)
    return groups

def fitness(groups, df):
    alpha, beta, gamma = 2.0, 1.0, 3.0
    scores = []
    features = ['hard_skills', 'soft_skills', 'creativity', 'teamwork']
    for group in groups:
        if len(group) < 5 or len(group) > 7:
            return -np.inf
        sub_df = df.loc[group]
        diversity_score = sub_df['gender'].nunique() + sub_df['nationality'].nunique()
        skill_coverage = sum(any(sub_df[f] > 4) for f in features)
        skill_balance = -sub_df[features].mean().std()
        score = alpha * diversity_score + beta * skill_coverage + gamma * skill_balance
        scores.append(score)
    return np.mean(scores)

def mutate(groups):
    g1, g2 = random.sample(range(len(groups)), 2)
    if groups[g1] and groups[g2]:
        i1 = random.choice(groups[g1])
        i2 = random.choice(groups[g2])
        groups[g1].remove(i1)
        groups[g1].append(i2)
        groups[g2].remove(i2)
        groups[g2].append(i1)
    return groups

def crossover(p1, p2):
    half = len(p1) // 2
    child = p1[:half] + p2[half:]
    seen = set()
    for g in child:
        unique = []
        for s in g:
            if s not in seen:
                unique.append(s)
                seen.add(s)
        g[:] = unique
    return child

def repair(groups):
    changed = True
    while changed:
        changed = False
        for g in groups:
            while len(g) > 7:
                s = g.pop()
                min_grp = min(groups, key=len)
                min_grp.append(s)
                changed = True
    return groups

@app.post("/generate-groups")
async def generate_groups(file: UploadFile = File(...)):
    df = pd.read_csv(BytesIO(await file.read()))
    if not REQUIRED_COLS.issubset(df.columns):
        return JSONResponse(status_code=400, content={"error": "Dataset missing required columns."})

    for col in ['gender', 'nationality']:
        df[col] = LabelEncoder().fit_transform(df[col])

    features = ["gender", "nationality", "age", "hard_skills", "soft_skills", "creativity", "teamwork"]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    results = run_algorithms(X_scaled, df, distance_metric="euclidean")
    evals = evaluate_algorithms(X_scaled, df, results, features)
    best_algo = max(evals, key=lambda x: x[1] if not np.isnan(x[1]) else -1)

    best_labels = [lbl for name, lbl in results if name == best_algo[0]][0]
    df['cluster'] = best_labels

    initial_groups = create_initial_groups(df)
    pop_size, generations = 30, 50
    population = [initial_groups.copy() for _ in range(pop_size)]
    best_ind, best_fit = None, -np.inf
    for _ in range(generations):
        fitness_scores = [fitness(ind, df) for ind in population]
        for fit, ind in zip(fitness_scores, population):
            if fit > best_fit:
                best_fit = fit
                best_ind = [g.copy() for g in ind]
        population = sorted([x for _, x in zip(fitness_scores, population)], reverse=True)[:int(pop_size * 0.3)]
        while len(population) < pop_size:
            p1, p2 = random.sample(population, 2)
            child = crossover(p1, p2)
            child = mutate(child)
            child = repair(child)
            population.append(child)

    groups_output = []
    for i, group in enumerate(best_ind):
        members = df.loc[group].to_dict(orient="records")
        groups_output.append({"group": i+1, "size": len(group), "members": members})

    return {"best_algorithm": best_algo[0], "groups": groups_output}

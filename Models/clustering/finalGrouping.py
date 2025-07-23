import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
from minisom import MiniSom
import gower
import matplotlib.pyplot as plt
import seaborn as sns
import random

CSV_PATH = "/workspaces/Stage/Datasets/students_dataset.csv"
REQUIRED_COLS = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class", "gender", "nationality", "age"}

# --- Load dataset ---
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    if not REQUIRED_COLS.issubset(df.columns):
        st.error(f"Dataset must include the following columns: {REQUIRED_COLS}")
        return pd.DataFrame()
    return df


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

    spectral = SpectralClustering(n_clusters=4, affinity='nearest_neighbors', random_state=42)
    results.append(("Spectral", spectral.fit_predict(X_scaled)))

    gmm = GaussianMixture(n_components=4, random_state=42)
    results.append(("GMM", gmm.fit_predict(X_scaled)))

    try:
        meanshift = MeanShift()
        ms_labels = meanshift.fit_predict(X_scaled)
        results.append(("MeanShift", ms_labels))
    except Exception:
        pass

    som = MiniSom(6, 6, X_scaled.shape[1], sigma=1.0, learning_rate=0.5)
    som.random_weights_init(X_scaled)
    som.train_random(X_scaled, 100)
    som_labels = np.array([som.winner(x)[0]*6 + som.winner(x)[1] for x in X_scaled])
    results.append(("MiniSom", som_labels))

    return results

# --- Genetic Algorithm Functions ---
def create_initial_groups(df, group_size_min=5, group_size_max=7):
    n_students = len(df)
    n_groups = max(1, n_students // group_size_min)
    groups = [[] for _ in range(n_groups)]
    for i, idx in enumerate(df.index):
        groups[i % n_groups].append(idx)
    return groups

def fitness(groups, df, group_size_min=5, group_size_max=7):
    alpha, beta, gamma = 2.0, 1.0, 3.0
    scores = []
    features = ['hard_skills', 'soft_skills', 'creativity', 'teamwork']
    for group in groups:
        if len(group) < group_size_min or len(group) > group_size_max:
            return -np.inf
        sub_df = df.loc[group]
        gender_diversity = sub_df['gender'].nunique()
        nationality_diversity = sub_df['nationality'].nunique()
        diversity_score = gender_diversity + nationality_diversity
        skill_coverage = sum(any(sub_df[f] > 4) for f in features)
        mean_skills = sub_df[features].mean(axis=0)
        skill_balance = -mean_skills.std()
        score = alpha * diversity_score + beta * skill_coverage + gamma * skill_balance
        scores.append(score)
    return np.mean(scores)

def mutate(groups, df, group_size_min=5, group_size_max=7):
    if len(groups) < 2:
        return groups
    g1, g2 = random.sample(range(len(groups)), 2)
    if groups[g1] and groups[g2]:
        i1 = random.choice(groups[g1])
        i2 = random.choice(groups[g2])
        groups[g1].remove(i1)
        groups[g1].append(i2)
        groups[g2].remove(i2)
        groups[g2].append(i1)
    return groups

def crossover(parent1, parent2):
    half = len(parent1) // 2
    child = parent1[:half] + parent2[half:]
    all_students = set(sum(child, []))
    n_students = sum(len(g) for g in child)
    missing = set(range(n_students)) - all_students
    for m in missing:
        smallest_group = min(child, key=len)
        smallest_group.append(m)
    seen = set()
    for g in child:
        unique = []
        for s in g:
            if s not in seen:
                unique.append(s)
                seen.add(s)
        g[:] = unique
    return child

def repair(groups, df, group_size_min=5, group_size_max=7):
    changed = True
    while changed:
        changed = False
        for g in groups:
            while len(g) > group_size_max:
                student_to_move = g.pop()
                receivers = [grp for grp in groups if len(grp) < group_size_min]
                min_grp = min(receivers, key=len) if receivers else min(groups, key=len)
                min_grp.append(student_to_move)
                changed = True
    return groups

# --- Main App ---
st.set_page_config(layout="wide")
st.title("🎯 Student Grouping with Clustering + GA Optimization")

df = load_data(CSV_PATH)
if df.empty:
    st.stop()

mode = st.radio("Choose dataset mode:", ["Full Dataset", "Random 1500 Sample", "By Class"])
if mode == "Full Dataset":
    df_selected = df.copy()
elif mode == "Random 1500 Sample":
    df_selected = df.sample(1500, random_state=42) if len(df) > 1500 else df.copy()
else:
    selected_class = st.selectbox("🎓 Select a Class", sorted(df["class"].unique()))
    df_selected = df[df["class"] == selected_class].reset_index(drop=True)

# --- Encode categorical features ---
for col in ['gender', 'nationality']:
    le = LabelEncoder()
    df_selected[col] = le.fit_transform(df_selected[col])

# --- Define features and scale ---
features = ["gender", "nationality", "age", "hard_skills", "soft_skills", "creativity", "teamwork"]
X = df_selected[features]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

distance_metric = st.selectbox("Select distance metric", ["euclidean", "cosine", "gower"])

st.markdown("### 🤖 Running Clustering Algorithms...")
results = run_algorithms(X_scaled, df_selected, distance_metric)
eval_data = []
for algo_name, labels in results:
    unique_labels = set(labels)
    if len(unique_labels) <= 1:
        continue
    try:
        sil = silhouette_score(X_scaled, labels) if distance_metric != 'gower' else silhouette_score(gower.gower_matrix(df_selected[features]), labels, metric='precomputed')
    except:
        sil = np.nan
    try:
        dbs = davies_bouldin_score(X_scaled, labels)
    except:
        dbs = np.nan
    ge, ne = gender_nationality_entropy(df_selected, labels)
    eval_data.append({"Algorithm": algo_name, "Silhouette Score": round(sil, 4) if sil == sil else "-", "Davies-Bouldin": round(dbs, 4) if dbs == dbs else "-", "Gender Entropy": round(ge, 4), "Nationality Entropy": round(ne, 4)})

results_df = pd.DataFrame(eval_data).sort_values(by="Silhouette Score", ascending=False)
# 📌 Find and display the best algorithm
valid_results = results_df.dropna()
if not valid_results.empty:
    best_row = valid_results.loc[valid_results["Silhouette Score"].idxmax()]
    st.success(f"""✅ **Best algorithm is `{best_row["Algorithm"]}`**  
- Silhouette Score = {best_row["Silhouette Score"]:.4f}  
""")
else:
    st.warning("No valid clustering results available to determine the best algorithm.")

# --- Dimensionality Reduction for Visualization ---
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X_scaled)

st.markdown("### Visual Comparison of Clustering Algorithms")
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes = axes.flatten()

for i, (algo_name, labels) in enumerate(results):
    if i >= 8: break
    unique_labels = set(labels)
    if len(unique_labels) <= 1:
        axes[i].axis('off')
        continue
    ax = axes[i]
    scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='tab20', s=15, alpha=0.7)
    ax.set_title(algo_name)
    ax.set_xticks([])
    ax.set_yticks([])

for j in range(i+1, len(axes)):
    axes[j].axis('off')

st.pyplot(fig)

st.subheader("Clustering Evaluation Metrics")
st.dataframe(results_df, use_container_width=True)

if not results_df.empty:
    best_algo = results_df.iloc[0]['Algorithm']
    best_labels = [lbl for name, lbl in results if name == best_algo][0]
    df_selected['cluster'] = best_labels

    st.subheader("📈 Cluster Distribution")
    fig2, ax2 = plt.subplots()
    sns.countplot(x="cluster", data=df_selected, ax=ax2)
    st.pyplot(fig2)

    st.subheader(f"🎯 Visualization of Best Algorithm Clusters: {best_algo}")
    fig3, ax3 = plt.subplots(figsize=(8,6))
    scatter = ax3.scatter(X_2d[:, 0], X_2d[:, 1], c=best_labels, cmap='tab20', s=30, alpha=0.8)
    legend1 = ax3.legend(*scatter.legend_elements(), title="Clusters", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.add_artist(legend1)
    ax3.set_xlabel("PCA Component 1")
    ax3.set_ylabel("PCA Component 2")
    ax3.set_title(f"Clusters by {best_algo}")
    st.pyplot(fig3)

    st.subheader("👫 Optimized Grouping with GA")
    if st.button("Run Genetic Algorithm Optimization"):
        initial_groups = create_initial_groups(df_selected)
        pop_size, generations = 30, 50
        population = [initial_groups.copy() for _ in range(pop_size)]
        best_individual, best_fitness = None, -np.inf
        for _ in range(generations):
            fitness_scores = []
            for individual in population:
                fit = fitness(individual, df_selected)
                fitness_scores.append(fit)
                if fit > best_fitness:
                    best_fitness = fit
                    best_individual = [g.copy() for g in individual]
            population = sorted([x for _, x in zip(fitness_scores, population)], reverse=True)[:int(pop_size*0.3)]
            while len(population) < pop_size:
                p1, p2 = random.sample(population, 2)
                child = crossover(p1, p2)
                child = mutate(child, df_selected)
                child = repair(child, df_selected)
                population.append(child)
        for i, group in enumerate(best_individual):
            st.markdown(f"#### Group {i+1} (Size: {len(group)})")
            st.dataframe(df_selected.loc[group][["first_name", "last_name", "gender", "nationality", "age"] + ["hard_skills", "soft_skills", "creativity", "teamwork"]])
        export_df = pd.concat([df_selected.loc[g].assign(group=i+1) for i, g in enumerate(best_individual)])
        st.download_button("⬇️ Download Optimized Groups CSV", export_df.to_csv(index=False).encode('utf-8'), "optimized_groups.csv", "text/csv")

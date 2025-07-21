import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns
import random

# --- Constants ---
CSV_PATH = "/workspaces/Stage/Datasets/students_dataset.csv"
REQUIRED_COLS = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class", "gender", "nationality"}

# --- Load dataset ---
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    if not REQUIRED_COLS.issubset(df.columns):
        st.error(f"Dataset must include the following columns: {REQUIRED_COLS}")
        return pd.DataFrame()
    return df

# --- Clustering Function ---
def try_all_clustering_models(X_scaled, max_k):
    results = {}

    for k in range(3, max_k + 1):
        # KMeans
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        if len(set(labels)) > 1:
            sil = silhouette_score(X_scaled, labels)
            db = davies_bouldin_score(X_scaled, labels)
            results[f"KMeans_{k}"] = (labels, sil, db)

        # Agglomerative
        agg = AgglomerativeClustering(n_clusters=k)
        labels = agg.fit_predict(X_scaled)
        if len(set(labels)) > 1:
            sil = silhouette_score(X_scaled, labels)
            db = davies_bouldin_score(X_scaled, labels)
            results[f"Agglomerative_{k}"] = (labels, sil, db)

        # Gaussian Mixture
        gmm = GaussianMixture(n_components=k, random_state=42)
        labels = gmm.fit_predict(X_scaled)
        if len(set(labels)) > 1:
            sil = silhouette_score(X_scaled, labels)
            db = davies_bouldin_score(X_scaled, labels)
            results[f"GMM_{k}"] = (labels, sil, db)

        # Spectral Clustering
        spectral = SpectralClustering(n_clusters=k, affinity='nearest_neighbors', random_state=42)
        labels = spectral.fit_predict(X_scaled)
        if len(set(labels)) > 1:
            sil = silhouette_score(X_scaled, labels)
            db = davies_bouldin_score(X_scaled, labels)
            results[f"Spectral_{k}"] = (labels, sil, db)

    # DBSCAN (only once, no k parameter)
    dbscan = DBSCAN(eps=0.4, min_samples=3)
    labels = dbscan.fit_predict(X_scaled)
    if len(set(labels)) > 1 and len(set(labels)) < len(X_scaled):
        sil = silhouette_score(X_scaled, labels)
        db = davies_bouldin_score(X_scaled, labels)
        results["DBSCAN"] = (labels, sil, db)

    return results

# --- Evaluate Clusters ---
def evaluate_clusters(clustered_df):
    group_sizes = clustered_df['cluster'].value_counts().sort_index()
    return group_sizes, group_sizes.max(), group_sizes.min(), group_sizes.std()

# --- Genetic Algorithm Functions ---

def create_initial_groups(df, group_size_min=5, group_size_max=7):
    """Assign students to groups roughly by cluster, ensuring group size constraints"""
    n_students = len(df)
    n_groups = max(1, n_students // group_size_min)
    groups = [[] for _ in range(n_groups)]
    
    # Assign students round-robin to groups (simple balanced start)
    for i, idx in enumerate(df.index):
        groups[i % n_groups].append(idx)
    return groups

def fitness(groups, df, group_size_min=5, group_size_max=7):
    alpha, beta, gamma, delta = 2.0, 1.0, 3.0, 5.0
    scores = []
    features = ['hard_skills', 'soft_skills', 'creativity', 'teamwork']
    for group in groups:
        if len(group) < group_size_min or len(group) > group_size_max:
            return -np.inf  # Strong penalty
        
        sub_df = df.loc[group]
        
        # Diversity: count unique genders & nationalities
        gender_diversity = sub_df['gender'].nunique()
        nationality_diversity = sub_df['nationality'].nunique()
        diversity_score = gender_diversity + nationality_diversity
        
        # Check if at least one person has score > 4 in each skill category
        skill_coverage = 0
        for f in features:
            if any(sub_df[f] > 4):
                skill_coverage += 1
        
        # Skill balance (std dev of mean skills)
        mean_skills = sub_df[features].mean(axis=0)
        skill_balance = -mean_skills.std()  # lower std better
        
        score = (
            alpha * diversity_score +
            beta * skill_coverage +
            gamma * skill_balance
        )
        scores.append(score)
    return np.mean(scores)

def mutate(groups, df, group_size_min=5, group_size_max=7):
    # Swap random students between two random groups
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
    # Simple crossover: first half from parent1, second half from parent2
    half = len(parent1) // 2
    child = parent1[:half] + parent2[half:]
    
    # Remove duplicates and fill missing
    all_students = set(sum(child, []))
    n_students = sum(len(g) for g in child)
    missing = set(range(n_students)) - all_students
    for m in missing:
        # Assign missing student to smallest group
        smallest_group = min(child, key=len)
        smallest_group.append(m)
    
    # Remove duplicates from groups keeping only first occurrence
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
    # Balance group sizes if needed (move students from large groups to small)
    changed = True
    while changed:
        changed = False
        for g in groups:
            while len(g) > group_size_max:
                student_to_move = g.pop()
                receivers = [grp for grp in groups if len(grp) < group_size_min]
                if receivers:
                    min_grp = min(receivers, key=len)
                    min_grp.append(student_to_move)
                else:
                    min_grp = min(groups, key=len)
                    min_grp.append(student_to_move)
                changed = True
    return groups

# --- Main App ---
st.set_page_config(layout="wide")
st.title("🎯 Student Grouping via Clustering + Genetic Algorithm")

df = load_data(CSV_PATH)
if df.empty:
    st.stop()

selected_class = st.selectbox("🎓 Select a Class", sorted(df["class"].unique()))
df_class = df[df["class"] == selected_class].reset_index(drop=True)

features = ['hard_skills', 'soft_skills', 'creativity', 'teamwork']
X = df_class[features]
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

st.markdown("### 🤖 Trying Multiple Clustering Models...")
results = try_all_clustering_models(X_scaled, max_k=min(10, len(df_class)//5))

if not results:
    st.error("❌ No valid clustering found.")
    st.stop()

summary = [(name, sil, db) for name, (_, sil, db) in results.items()]
results_df = pd.DataFrame(summary, columns=["Model", "Silhouette Score", "Davies-Bouldin"])
st.dataframe(results_df.sort_values("Silhouette Score", ascending=False))

best_model = results_df.sort_values("Silhouette Score", ascending=False).iloc[0]["Model"]
st.success(f"✅ Best clustering model: `{best_model}`")

best_labels = results[best_model][0]
df_class["cluster"] = best_labels

st.subheader("📦 Cluster Balance")
group_sizes, max_size, min_size, std_dev = evaluate_clusters(df_class)
st.write(f"Group Sizes: {group_sizes.to_dict()}")
st.write(f"Max: {max_size}, Min: {min_size}, Std Dev: {std_dev:.2f}")

st.subheader("📈 Cluster Distribution")
fig, ax = plt.subplots()
sns.countplot(x="cluster", data=df_class, ax=ax)
ax.set_title("Number of Students per Cluster")
st.pyplot(fig)

st.subheader("👥 Clustered Students")
st.dataframe(df_class[["first_name", "last_name", "cluster"] + features])

group_size = st.slider("👫 Group Size", 5, 7, 6)
n_groups = len(df_class) // group_size

if st.button("📚 Form & Optimize Groups with GA"):
    # Initial groups from cluster assignment indices (just roughly grouped)
    init_groups = create_initial_groups(df_class, group_size_min=5, group_size_max=7)

    pop_size = 30
    generations = 50

    # Create initial population (all copies of initial groups for simplicity)
    population = [init_groups.copy() for _ in range(pop_size)]

    best_individual = None
    best_fitness = -np.inf

    for gen in range(generations):
        # Evaluate fitness
        fitness_scores = []
        for individual in population:
            fit = fitness(individual, df_class, group_size_min=5, group_size_max=7)
            fitness_scores.append(fit)
            if fit > best_fitness:
                best_fitness = fit
                best_individual = [g.copy() for g in individual]

        # Selection: keep top 30%
        sorted_pop = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]
        population = sorted_pop[:int(pop_size*0.3)]

        # Generate children with crossover and mutation
        while len(population) < pop_size:
            p1, p2 = random.sample(population[:max(2, int(pop_size*0.3))], 2)
            child = crossover(p1, p2)
            child = mutate(child, df_class)
            child = repair(child, df_class, group_size_min=5, group_size_max=7)
            population.append(child)

    # Show best grouping result
    group_dfs = [df_class.loc[g].reset_index(drop=True) for g in best_individual]

    for i, group_df in enumerate(group_dfs, 1):
        st.markdown(f"#### 🧠 Group {i} (Size: {len(group_df)})")
        st.dataframe(group_df[["first_name", "last_name", "gender", "nationality"] + features])

    # Export
    export_df = pd.concat([g.assign(group=i+1) for i, g in enumerate(group_dfs)])
    csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Optimized Groups CSV", csv, f"{selected_class}_optimized_groups.csv", "text/csv")

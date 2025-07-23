import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering, MeanShift
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from minisom import MiniSom
import gower
import matplotlib.pyplot as plt
import seaborn as sns
import random

# Constants
CSV_PATH = "/workspaces/Stage/Datasets/students_dataset.csv"
REQUIRED_COLS = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class", "gender", "nationality"}

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

    # KMeans
    kmeans = KMeans(n_clusters=4, random_state=42)
    kmeans_labels = kmeans.fit_predict(X_scaled)
    results.append(("KMeans", kmeans_labels))

    # AgglomerativeClustering with metric param
    agg = AgglomerativeClustering(n_clusters=4, metric='euclidean', linkage='ward')
    agg_labels = agg.fit_predict(X_scaled)
    results.append(("Agglomerative", agg_labels))

    # DBSCAN
    dbscan = DBSCAN(metric=distance_metric if distance_metric != 'gower' else 'precomputed', eps=0.6, min_samples=5)
    if distance_metric == 'gower':
        dist_mat = gower.gower_matrix(df[list(REQUIRED_COLS - {"first_name", "last_name"})])
        db_labels = dbscan.fit_predict(dist_mat)
    else:
        db_labels = dbscan.fit_predict(X_scaled)
    results.append(("DBSCAN", db_labels))

    # SpectralClustering
    spectral = SpectralClustering(n_clusters=4, affinity='nearest_neighbors', random_state=42)
    spectral_labels = spectral.fit_predict(X_scaled)
    results.append(("Spectral", spectral_labels))

    # Gaussian Mixture Model
    gmm = GaussianMixture(n_components=4, random_state=42)
    gmm_labels = gmm.fit_predict(X_scaled)
    results.append(("GMM", gmm_labels))

    # MeanShift
    meanshift = MeanShift()
    try:
        ms_labels = meanshift.fit_predict(X_scaled)
        results.append(("MeanShift", ms_labels))
    except Exception:
        pass

    # MiniSom
    som = MiniSom(6, 6, X_scaled.shape[1], sigma=1.0, learning_rate=0.5)
    som.random_weights_init(X_scaled)
    som.train_random(X_scaled, 100)
    som_labels = np.array([som.winner(x)[0]*6 + som.winner(x)[1] for x in X_scaled])
    results.append(("MiniSom", som_labels))

    return results

# Main app
st.set_page_config(layout="wide")
st.title("🎯 Student Grouping Clustering & Evaluation")

df = load_data(CSV_PATH)
if df.empty:
    st.stop()

mode = st.radio("Choose dataset mode:", ["Full Dataset", "Random 1500 Sample", "By Class"])

if mode == "Full Dataset":
    df_selected = df.copy()
elif mode == "Random 1500 Sample":
    if len(df) > 1500:
        df_selected = df.sample(1500, random_state=42)
    else:
        df_selected = df.copy()
else:
    selected_class = st.selectbox("🎓 Select a Class", sorted(df["class"].unique()))
    df_selected = df[df["class"] == selected_class].reset_index(drop=True)

numeric_features = ["hard_skills", "soft_skills", "creativity", "teamwork"]
X = df_selected[numeric_features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

distance_metric = st.selectbox("Select distance metric", ["euclidean", "cosine", "gower"])

st.markdown("### 🤖 Running Clustering Algorithms...")

results = run_algorithms(X_scaled, df_selected, distance_metric)

eval_data = []
for algo_name, labels in results:
    # Skip if all one cluster or too few clusters
    unique_labels = set(labels)
    if len(unique_labels) <= 1 or (distance_metric == "gower" and -1 in unique_labels and len(unique_labels) == 2):
        continue
    try:
        metric_for_sil = distance_metric if distance_metric != "gower" else "precomputed"
        if metric_for_sil == "precomputed":
            dist_mat = gower.gower_matrix(df_selected[numeric_features])
            sil = silhouette_score(dist_mat, labels, metric=metric_for_sil)
        else:
            sil = silhouette_score(X_scaled, labels, metric=metric_for_sil)
    except:
        sil = np.nan
    try:
        dbs = davies_bouldin_score(X_scaled, labels)
    except:
        dbs = np.nan
    ge, ne = gender_nationality_entropy(df_selected, labels)
    eval_data.append({
        "Algorithm": algo_name,
        "Silhouette Score": round(sil, 4) if sil == sil else "-",
        "Davies-Bouldin": round(dbs, 4) if dbs == dbs else "-",
        "Gender Entropy": round(ge, 4) if ge == ge else "-",
        "Nationality Entropy": round(ne, 4) if ne == ne else "-"
    })

results_df = pd.DataFrame(eval_data).sort_values(by="Silhouette Score", ascending=False)
st.subheader("Clustering Evaluation Metrics")
st.dataframe(results_df, use_container_width=True)

if not results_df.empty:
    best_algo = results_df.iloc[0]
    st.success(f"Best algorithm based on Silhouette Score: {best_algo['Algorithm']} ({best_algo['Silhouette Score']})")

    # Plot cluster distribution for best algorithm
    best_labels = None
    for algo_name, labels in results:
        if algo_name == best_algo['Algorithm']:
            best_labels = labels
            break

    if best_labels is not None:
        df_selected["cluster"] = best_labels
        st.subheader("📈 Cluster Distribution")
        fig, ax = plt.subplots()
        sns.countplot(x="cluster", data=df_selected, ax=ax)
        ax.set_title(f"Number of Students per Cluster ({best_algo['Algorithm']})")
        st.pyplot(fig)

        st.subheader("👥 Clustered Students")
        st.dataframe(df_selected[["first_name", "last_name", "cluster"] + numeric_features])
else:
    st.info("No valid clustering results to show.")

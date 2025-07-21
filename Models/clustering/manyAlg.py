import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns

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

# --- Form Heterogeneous Groups ---
def form_groups(df, n_groups):
    df_sorted = df.sort_values(by=['hard_skills', 'soft_skills', 'creativity', 'teamwork'], ascending=[False]*4).reset_index(drop=True)
    groups = [[] for _ in range(n_groups)]
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        groups[i % n_groups].append(row)
    return [pd.DataFrame(group) for group in groups]

# --- Main App ---
st.set_page_config(layout="wide")
st.title("🎯 Student Grouping via Clustering")

df = load_data(CSV_PATH)

if not df.empty:
    selected_class = st.selectbox("🎓 Select a Class", sorted(df["class"].unique()))
    df_class = df[df["class"] == selected_class].copy().reset_index(drop=True)
    st.write(f"✅ {len(df_class)} students found in class `{selected_class}`.")

    features = ['hard_skills', 'soft_skills', 'creativity', 'teamwork']
    X = df_class[features]
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    st.markdown("### 🤖 Trying Multiple Clustering Models...")
    results = try_all_clustering_models(X_scaled, max_k=min(10, len(df_class)//5))

    if not results:
        st.error("❌ No valid clustering found.")
    else:
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

        if st.button("📚 Form Heterogeneous Groups"):
            groups = form_groups(df_class, n_groups)
            for i, group_df in enumerate(groups):
                st.markdown(f"#### 🧠 Group {i+1}")
                st.dataframe(group_df[["first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork"]])

            export_df = pd.concat([group.assign(group=i+1) for i, group in enumerate(groups)])
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Grouped CSV", csv, f"{selected_class}_grouped.csv", "text/csv")

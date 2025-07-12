import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns
import random
from collections import defaultdict

st.set_page_config(layout="wide")
st.header("🧠 Clustering & Heterogeneous Group Formation from CSV")

CSV_PATH = "/workspaces/Stage/Models/clustering/synthetic_students.csv"

# --- Load CSV ---
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Failed to load CSV file at {CSV_PATH}: {e}")
    st.stop()

st.subheader("📊 Loaded Student Data")
st.dataframe(df)

# --- Check required columns ---
required_cols = {"Name", "Hard Skills", "Soft Skills", "Creativity", "Teamwork"}
if not required_cols.issubset(set(df.columns)):
    st.error(f"CSV must contain columns: {required_cols}")
    st.stop()

student_names = df["Name"].tolist()
score_vectors = df[["Hard Skills", "Soft Skills", "Creativity", "Teamwork"]].values

if len(score_vectors) < 4:
    st.warning("🚫 Not enough students to form 4 clusters.")
    st.stop()

# ---------- Clustering ----------
kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
labels = kmeans.fit_predict(score_vectors)
df["Cluster"] = labels

# ---------- PCA Visualisation ----------
pca = PCA(n_components=2)
pca_result = pca.fit_transform(score_vectors)
df["PCA1"] = pca_result[:, 0]
df["PCA2"] = pca_result[:, 1]

st.subheader("📉 PCA Visualization of Clusters")
fig, ax = plt.subplots()
sns.scatterplot(data=df, x="PCA1", y="PCA2", hue="Cluster", palette="tab10", s=100, ax=ax)
st.pyplot(fig)

# ---------- WCSS ----------
st.subheader("📈 Clustering Compactness (WCSS - Inertia)")
st.write(f"**Within-Cluster Sum of Squares (WCSS):** {kmeans.inertia_:.2f}")

# ---------- Clustering Quality Metrics ----------
st.subheader("📐 Clustering Quality Metrics")
silhouette = silhouette_score(score_vectors, labels)
calinski = calinski_harabasz_score(score_vectors, labels)
davies = davies_bouldin_score(score_vectors, labels)
st.markdown(f"""
- **Silhouette Score:** `{silhouette:.3f}` (range: -1 to 1, higher is better)
- **Calinski-Harabasz Index:** `{calinski:.2f}` (higher is better)
- **Davies-Bouldin Index:** `{davies:.3f}` (lower is better)
""")

# ---------- Cluster Distribution ----------
st.subheader("📌 Cluster Size Distribution")
cluster_counts = df["Cluster"].value_counts().sort_index()
st.bar_chart(cluster_counts)

# ---------- Cluster Skill Averages ----------
st.subheader("📊 Average Skill Scores per Cluster")
cluster_means = df.groupby("Cluster")[["Hard Skills", "Soft Skills", "Creativity", "Teamwork"]].mean()
st.dataframe(cluster_means.style.format("{:.2f}"))

# ---------- Color Coded Clusters ----------
def highlight_clusters(val):
    colors = ['#FFCDD2', '#C8E6C9', '#BBDEFB', '#FFF9C4']
    return f'background-color: {colors[val % len(colors)]}' if not pd.isna(val) else ''

st.subheader("🎯 Students with Cluster Assignments (Color Coded)")
styled_df = df[["Name", "Hard Skills", "Soft Skills", "Creativity", "Teamwork", "Cluster"]].style.applymap(
    highlight_clusters, subset=["Cluster"]
)
st.dataframe(styled_df)

# ---------- Group Formation ----------
cluster_map = defaultdict(list)
for i, label in enumerate(labels):
    cluster_map[label].append(student_names[i])
for cl in cluster_map:
    random.shuffle(cluster_map[cl])

groups = []
while all(cluster_map[cl] for cl in cluster_map):
    group = [cluster_map[cl].pop(0) for cl in range(4)]
    groups.append(group)

st.success(f"✅ Created {len(groups)} heterogeneous groups (4 students per group):")
for i, g in enumerate(groups):
    st.markdown(f"**Group {i+1}:** " + ", ".join(g))

# ---------- Group Skill Averages ----------
st.subheader("📏 Group Skill Averages")
group_skill_averages = []
fairness_scores = []

for group in groups:
    group_scores = df[df["Name"].isin(group)][["Hard Skills", "Soft Skills", "Creativity", "Teamwork"]]
    group_mean = group_scores.mean().to_dict()
    group_std = group_scores.std().mean()  # Fairness: average std across all skills
    group_mean["Fairness (Avg Std)"] = group_std
    group_mean["Group"] = f"Group {groups.index(group)+1}"
    group_skill_averages.append(group_mean)
    fairness_scores.append(group_std)

group_avg_df = pd.DataFrame(group_skill_averages).set_index("Group")
st.dataframe(group_avg_df.style.format("{:.2f}"))

# ---------- Group Balance Visualization ----------
st.subheader("🧪 Group Skill Balance Comparison")
fig, ax = plt.subplots(figsize=(10, 4))
group_avg_df.drop(columns=["Fairness (Avg Std)"]).plot(kind='bar', ax=ax)
plt.xticks(rotation=45)
plt.ylabel("Average Score")
plt.title("Skill Distribution per Group")
st.pyplot(fig)

# ---------- Fairness Visualization ----------
st.subheader("⚖️ Group Fairness Metric (Lower is More Balanced)")
fig2, ax2 = plt.subplots()
ax2.bar(group_avg_df.index, group_avg_df["Fairness (Avg Std)"])
ax2.set_ylabel("Average Standard Deviation")
ax2.set_title("Group Fairness (Variability in Skill Levels)")
st.pyplot(fig2)

# ---------- Export Groups ----------
group_df = pd.DataFrame(groups, columns=["Student 1", "Student 2", "Student 3", "Student 4"])
csv = group_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Formed Groups as CSV", csv, "heterogeneous_groups.csv", "text/csv")

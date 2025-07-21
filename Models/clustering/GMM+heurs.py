import streamlit as st
import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🤖 Group Formation: GMM Clustering + Heuristic Grouping")

CSV_PATH = "/workspaces/Stage/Datasets/students_dataset.csv"

# Load dataset
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Failed to load CSV file: {e}")
    st.stop()

required_cols = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class", "gender", "nationality"}
if not required_cols.issubset(df.columns):
    st.error(f"CSV must contain columns: {required_cols}")
    st.stop()

df["class"] = df["class"].astype(str).str.strip()
unique_classes = sorted(df["class"].unique())
selected_class = st.selectbox("🎓 Select class to group students from:", unique_classes)

class_df = df[df["class"] == selected_class].reset_index(drop=True)
if class_df.empty:
    st.warning("No students in selected class.")
    st.stop()

class_df["Name"] = class_df["first_name"] + " " + class_df["last_name"]

st.subheader(f"Students in Class: {selected_class}")
st.dataframe(class_df[["Name", "gender", "nationality", "hard_skills", "soft_skills", "creativity", "teamwork"]])

skill_cols = ["hard_skills", "soft_skills", "creativity", "teamwork"]

# Scale skills for clustering
scaler = MinMaxScaler()
scaled_skills = scaler.fit_transform(class_df[skill_cols])

# Determine number of groups
MIN_GROUP_SIZE = 5
MAX_GROUP_SIZE = 7
num_students = len(class_df)
num_groups = int(np.ceil(num_students / MIN_GROUP_SIZE))
default_k = num_groups  # baseline number of clusters

# Run GMM clustering with best k selection
best_sil = -1
best_dbi = float("inf")
best_k = None
silhouette_scores = []
dbi_scores = []
k_values = list(range(2, min(num_students, 11)))  # k from 2 to 10 or num_students

for k in k_values:
    gmm = GaussianMixture(n_components=k, random_state=42)
    labels = gmm.fit_predict(scaled_skills)
    try:
        sil = silhouette_score(scaled_skills, labels)
        dbi = davies_bouldin_score(scaled_skills, labels)
        silhouette_scores.append(sil)
        dbi_scores.append(dbi)
        if sil > best_sil:
            best_sil = sil
            best_dbi = dbi
            best_k = k
    except Exception:
        silhouette_scores.append(None)
        dbi_scores.append(None)

# Show best results
st.subheader("📈 Best Clustering Evaluation")
st.markdown(f"- ✅ Best **Silhouette Score**: **{best_sil:.3f}** at **k = {best_k}**")
st.markdown(f"- ✅ Corresponding **Davies-Bouldin Index**: **{best_dbi:.3f}**")

# Plot metrics across k
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# Silhouette
ax[0].plot(k_values, silhouette_scores, marker='o', color='green')
ax[0].set_title("Silhouette Score vs. k")
ax[0].set_xlabel("Number of Clusters (k)")
ax[0].set_ylabel("Silhouette Score")

# DBI
ax[1].plot(k_values, dbi_scores, marker='o', color='blue')
ax[1].set_title("Davies-Bouldin Index vs. k")
ax[1].set_xlabel("Number of Clusters (k)")
ax[1].set_ylabel("Davies-Bouldin Index (lower is better)")

st.pyplot(fig)

# Use best_k for final clustering and grouping
gmm = GaussianMixture(n_components=best_k, random_state=42)
clusters = gmm.fit_predict(scaled_skills)
class_df['Cluster'] = clusters

# Recompute number of groups
num_groups = best_k

# Initialize empty groups
groups = [[] for _ in range(num_groups)]

# Create cluster → student mapping
cluster_dict = {c: class_df[class_df['Cluster'] == c].index.tolist() for c in range(best_k)}
import itertools
cluster_iters = {c: iter(members) for c, members in cluster_dict.items()}

group_idx = 0
done = False
while not done:
    done = True
    for c in range(best_k):
        try:
            student_idx = next(cluster_iters[c])
            groups[group_idx].append(student_idx)
            group_idx = (group_idx + 1) % num_groups
            done = False
        except StopIteration:
            pass

# Fix group sizes
def fix_group_sizes(groups, min_size=MIN_GROUP_SIZE, max_size=MAX_GROUP_SIZE):
    small_groups = [g for g in groups if len(g) < min_size]
    valid_groups = [g for g in groups if len(g) >= min_size]

    for sg in small_groups:
        members = list(sg)
        for member in members:
            placed = False
            for vg in valid_groups:
                if len(vg) < max_size:
                    vg.append(member)
                    placed = True
                    break
            if placed:
                sg.remove(member)

    groups = [g for g in groups if len(g) > 0]

    # Merge leftover small groups
    while True:
        small_groups = [g for g in groups if len(g) < min_size]
        if not small_groups or len(groups) == 1:
            break
        small_groups = sorted(small_groups, key=len)
        g1 = small_groups[0]
        g2 = small_groups[1] if len(small_groups) > 1 else None
        if g2 is None:
            break
        groups.remove(g1)
        groups.remove(g2)
        merged = g1 + g2
        groups.append(merged)

    return groups

groups = fix_group_sizes(groups)

# Assign students to groups
group_rows = []
for gid, g in enumerate(groups, start=1):
    for idx in g:
        row = class_df.loc[idx].copy()
        row["Group"] = f"Group {gid}"
        group_rows.append(row)

result_df = pd.DataFrame(group_rows)

# Final output
st.subheader("🧑‍🤝‍🧑 Final Groups with Cluster Mixing")
st.dataframe(result_df[["Group", "Name", "gender", "nationality", "Cluster", *skill_cols]])

# Skill variance
skill_var = result_df.groupby("Group")[skill_cols].var()
st.subheader("⚖️ Skill Variance per Group")
st.dataframe(skill_var.style.format("{:.3f}"))

# Demographic diversity
gender_div = result_df.groupby("Group")["gender"].nunique()
nat_div = result_df.groupby("Group")["nationality"].nunique()
diversity_df = pd.DataFrame({
    "Gender Diversity": gender_div,
    "Nationality Diversity": nat_div
})
st.subheader("🌍 Demographic Diversity per Group")
st.dataframe(diversity_df)

# Group sizes
group_sizes = result_df.groupby("Group").size()
st.subheader("📏 Group Sizes")
st.dataframe(group_sizes.rename("Size"))

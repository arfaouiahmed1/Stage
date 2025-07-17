import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import SpectralClustering, AgglomerativeClustering

st.set_page_config(layout="wide")
st.title("🔍 Grouping Students using Clustering Algorithms")

CSV_PATH = "/workspaces/Stage/Datasets/students_train.csv"

# --- Load Data ---
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

required_cols = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class"}
if not required_cols.issubset(df.columns):
    st.error(f"Missing columns: {required_cols - set(df.columns)}")
    st.stop()

# --- Class Filter ---
classes = sorted(df["class"].unique())
selected_class = st.selectbox("🎓 Select a class", classes)

df = df[df["class"] == selected_class].reset_index(drop=True)
if df.empty:
    st.warning("No students found for this class.")
    st.stop()

df["Name"] = df["first_name"] + " " + df["last_name"]
st.subheader("👥 Students")
st.dataframe(df[["Name", "hard_skills", "soft_skills", "creativity", "teamwork"]])

# --- Preprocessing ---
X_raw = df[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].values
scaler = StandardScaler()
X = scaler.fit_transform(X_raw)

# --- Group Settings ---
num_students = len(df)
k = st.slider("🔢 Number of groups", min_value=2, max_value=min(10, num_students), value=3)

# --- Clustering Choice ---
clustering_method = st.selectbox("🧠 Choose clustering algorithm", ["Spectral Clustering", "Agglomerative Clustering"])

if clustering_method == "Spectral Clustering":
    model = SpectralClustering(n_clusters=k, affinity='nearest_neighbors', random_state=42, assign_labels="kmeans")
elif clustering_method == "Agglomerative Clustering":
    model = AgglomerativeClustering(n_clusters=k, linkage='ward')

# --- Run Clustering ---
labels = model.fit_predict(X)
df['Group'] = labels + 1  # to start group numbering from 1

# --- Group Display ---
def highlight_group(val):
    colors = ['#FFCDD2', '#C8E6C9', '#BBDEFB', '#FFF9C4', '#D1C4E9', '#B2DFDB', '#F8BBD0', '#DCEDC8', '#FFE0B2', '#CFD8DC']
    return f'background-color: {colors[(val-1) % len(colors)]}' if pd.notnull(val) else ''

st.subheader(f"📋 Groups formed using {clustering_method}")
st.dataframe(df[['Group', 'Name', 'hard_skills', 'soft_skills', 'creativity', 'teamwork']].style.applymap(highlight_group, subset=['Group']))

# --- Stats ---
st.subheader("📊 Average skill per group")
group_stats = df.groupby('Group')[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].mean()
st.dataframe(group_stats.style.format("{:.2f}"))

st.subheader("⚖️ Standard deviation per group (heterogeneity indicator)")
group_std = df.groupby('Group')[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].std()
group_std['Avg Std'] = group_std.mean(axis=1)
st.dataframe(group_std[['Avg Std']].style.format("{:.3f}"))

# --- Export CSV ---
grouped_export = df.groupby('Group')['Name'].apply(list).reset_index()
longest_group = grouped_export['Name'].apply(len).max()
export_df = pd.DataFrame(grouped_export['Name'].to_list(), columns=[f"Student {i+1}" for i in range(longest_group)])
csv_data = export_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download grouped students", csv_data, f"clustered_groups_{selected_class}.csv", "text/csv")

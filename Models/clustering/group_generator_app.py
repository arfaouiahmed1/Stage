import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import random
from collections import defaultdict

st.header("🧠 Clustering & Heterogeneous Group Formation from CSV")

CSV_PATH = "/workspaces/Stage/Models/clustering/synthetic_students.csv"

try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Failed to load CSV file at {CSV_PATH}: {e}")
    st.stop()

st.subheader("📊 Loaded Student Data")
st.dataframe(df)

required_cols = {"Name", "Hard Skills", "Soft Skills", "Creativity", "Teamwork"}
if not required_cols.issubset(set(df.columns)):
    st.error(f"CSV must contain columns: {required_cols}")
    st.stop()

student_names = df["Name"].tolist()
score_vectors = df[["Hard Skills", "Soft Skills", "Creativity", "Teamwork"]].values

if len(score_vectors) < 4:
    st.warning("🚫 Not enough students to form 4 clusters.")
else:
    kmeans = KMeans(n_clusters=4, random_state=42)
    labels = kmeans.fit_predict(score_vectors)
    
    # Add cluster labels to dataframe
    df["Cluster"] = labels
    st.subheader("🎯 Students with Cluster Assignments")
    st.dataframe(df[["Name", "Hard Skills", "Soft Skills", "Creativity", "Teamwork", "Cluster"]])

    # Group students by cluster
    cluster_map = defaultdict(list)
    for i, label in enumerate(labels):
        cluster_map[label].append(student_names[i])

    # Shuffle each cluster to randomize groups
    for cl in cluster_map:
        random.shuffle(cluster_map[cl])

    groups = []
    # While all clusters have at least one student left
    while all(cluster_map[cl] for cl in cluster_map):
        group = []
        for cl in range(4):
            group.append(cluster_map[cl].pop(0))
        groups.append(group)

    st.success(f"✅ Created {len(groups)} heterogeneous groups (4 students per group):")
    for i, g in enumerate(groups):
        st.markdown(f"**Group {i+1}:** " + ", ".join(g))

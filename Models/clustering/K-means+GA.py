import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import random

st.set_page_config(layout="wide")
st.title("🤖 Hybrid Group Formation: Clustering + GA with Repair")

CSV_PATH = "/workspaces/Stage/Datasets/students_dataset.csv"

# --- Load data ---
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

required_cols = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class", "gender", "nationality"}
if not required_cols.issubset(df.columns):
    st.error(f"The CSV must contain the columns: {required_cols}")
    st.stop()

unique_classes = sorted(df["class"].unique())
selected_class = st.selectbox("🎓 Select a class to group students from:", unique_classes)

filtered_df = df[df["class"] == selected_class].reset_index(drop=True)
if filtered_df.empty:
    st.warning("No students found for the selected class.")
    st.stop()

filtered_df["Name"] = filtered_df["first_name"] + " " + filtered_df["last_name"]

features_raw = filtered_df[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].values
scaler = MinMaxScaler()
features = scaler.fit_transform(features_raw)

num_students = len(filtered_df)
group_size_min, group_size_max = 5, 7
num_groups = int(np.ceil(num_students / group_size_min))

# --- Step 1: KMeans clustering ---
kmeans = KMeans(n_clusters=num_groups, random_state=42, n_init='auto')
clusters = kmeans.fit_predict(features)
filtered_df['Cluster'] = clusters

# --- Step 2: Evaluate clustering only ---
sil_score = silhouette_score(features, clusters)
db_score = davies_bouldin_score(features, clusters)

st.subheader("🔍 Initial Clustering (KMeans)")
st.dataframe(filtered_df[['Name', 'Cluster', 'hard_skills', 'soft_skills', 'creativity', 'teamwork']])

st.subheader("📈 Clustering Metrics")
st.metric("Silhouette Score (Higher is Better)", f"{sil_score:.3f}")
st.metric("Davies-Bouldin Index (Lower is Better)", f"{db_score:.3f}")

# --- Step 3: Initialize groups from clustering ---
initial_groups = [set() for _ in range(num_groups)]
for idx, cluster_label in enumerate(clusters):
    initial_groups[cluster_label].add(idx)

def fix_group_sizes(groups, min_size=5, max_size=7):
    changed = True
    while changed:
        changed = False
        for g in groups:
            while len(g) > max_size:
                student_to_move = g.pop()
                possible_receivers = [grp for grp in groups if len(grp) < min_size or len(grp) < max_size]
                if not possible_receivers:
                    receiver = min(groups, key=len)
                else:
                    receiver = min(possible_receivers, key=len)
                receiver.add(student_to_move)
                changed = True
        for g in groups:
            while len(g) < min_size:
                donor_groups = [grp for grp in groups if len(grp) > max_size]
                if not donor_groups:
                    break
                donor = max(donor_groups, key=len)
                student_to_move = donor.pop()
                g.add(student_to_move)
                changed = True
    return groups

def create_individual():
    groups = [set(g) for g in initial_groups]
    assigned = set().union(*groups)
    missing = set(range(num_students)) - assigned
    for student in missing:
        smallest = min(groups, key=len)
        smallest.add(student)
    groups = fix_group_sizes(groups, group_size_min, group_size_max)
    return groups

def diversity_score(group, df):
    genders = df.loc[list(group), 'gender'].nunique()
    nationalities = df.loc[list(group), 'nationality'].nunique()
    return genders + nationalities

def fitness(grouping):
    alpha, beta, gamma, delta = 1.5, 0.3, 0.3, 3.0
    scores = []
    for group in grouping:
        group_feats = features[list(group)]
        size = len(group)
        size_penalty = 0
        if size < group_size_min or size > group_size_max:
            size_penalty = -delta * abs(size - ((group_size_min + group_size_max)/2))
        if len(group_feats) > 1:
            mean_skill = np.mean(np.mean(group_feats, axis=0))
            std_dev = np.mean(np.std(group_feats, axis=0))
        else:
            mean_skill = 0
            std_dev = 5
        skills_present = [any(filtered_df.loc[list(group), skill] > 3) for skill in ['hard_skills', 'soft_skills', 'creativity', 'teamwork']]
        skill_penalty = -delta * (4 - sum(skills_present))
        div_score = diversity_score(group, filtered_df)
        score = alpha * mean_skill - beta * std_dev + gamma * div_score + size_penalty + skill_penalty
        scores.append(score)
    return np.mean(scores)

def repair(groups):
    all_assigned = []
    for g in groups:
        all_assigned.extend(g)
    counts = {}
    for s in all_assigned:
        counts[s] = counts.get(s, 0) + 1
    duplicates = [s for s, c in counts.items() if c > 1]
    missing = set(range(num_students)) - set(all_assigned)
    for d in duplicates:
        occurrences = 0
        for g in groups:
            if d in g:
                occurrences += 1
                if occurrences > 1:
                    g.remove(d)
    for m in missing:
        for g in groups:
            if len(g) < group_size_max:
                g.add(m)
                break
    return fix_group_sizes(groups, group_size_min, group_size_max)

def mutate(individual):
    if len(individual) < 2:
        return individual
    g1, g2 = random.sample(range(len(individual)), 2)
    if individual[g1] and individual[g2]:
        i1 = random.choice(tuple(individual[g1]))
        i2 = random.choice(tuple(individual[g2]))
        individual[g1].remove(i1)
        individual[g1].add(i2)
        individual[g2].remove(i2)
        individual[g2].add(i1)
    return repair(individual)

def crossover(p1, p2):
    all_indices = set(range(num_students))
    combined = list(p1[:len(p1)//2]) + list(p2[len(p2)//2:])
    seen = set()
    new_groups = []
    for group in combined:
        valid_group = set()
        for idx in group:
            if idx not in seen and len(valid_group) < group_size_max:
                valid_group.add(idx)
                seen.add(idx)
        if len(valid_group) >= group_size_min:
            new_groups.append(valid_group)
    left = list(all_indices - seen)
    for i in range(0, len(left), group_size_max):
        chunk = set(left[i:i + group_size_max])
        if len(chunk) >= group_size_min:
            new_groups.append(chunk)
    return repair(new_groups)

# --- Run Genetic Algorithm ---
pop_size = 50
num_gen = 100
population = [create_individual() for _ in range(pop_size)]

for generation in range(num_gen):
    population.sort(key=fitness, reverse=True)
    next_gen = population[:5]
    while len(next_gen) < pop_size:
        p1, p2 = random.sample(population[:15], 2)
        child = mutate(crossover(p1, p2))
        next_gen.append(child)
    population = next_gen

best_solution = population[0]

# --- Step 4: Final Evaluation and Display ---

labels = np.empty(num_students, dtype=int)
for g_id, group in enumerate(best_solution):
    for idx in group:
        labels[idx] = g_id

sil_score_final = silhouette_score(features, labels)
db_score_final = davies_bouldin_score(features, labels)

group_rows = []
for g_id, group in enumerate(best_solution, start=1):
    for idx in group:
        row = filtered_df.iloc[idx].to_dict()
        row['Group'] = g_id
        row['Name'] = f"{row['first_name']} {row['last_name']}"
        group_rows.append(row)

groups_df = pd.DataFrame(group_rows)

st.subheader(f"📋 Final Groups for class {selected_class}")
st.dataframe(groups_df[['Group', 'Name', 'hard_skills', 'soft_skills', 'creativity', 'teamwork']])

st.subheader("📊 Group Skill Averages")
st.dataframe(groups_df.groupby('Group')[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].mean().style.format("{:.2f}"))

st.subheader("⚖️ Group Balance (Standard Deviation)")
group_std = groups_df.groupby('Group')[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].std()
group_std['Avg Std'] = group_std.mean(axis=1)
st.dataframe(group_std[['Avg Std']].style.format("{:.3f}"))

st.subheader("🧮 Group Balance Index (Heterogeneity)")
balance_index = group_std['Avg Std'].mean()
st.metric("Group Balance Index (Lower is Better)", f"{balance_index:.3f}")

st.subheader("🌍 Group Diversity Overview")
gender_diversity = groups_df.groupby('Group')['gender'].nunique().rename('Gender Diversity')
nationality_diversity = groups_df.groupby('Group')['nationality'].nunique().rename('Nationality Diversity')
diversity_df = pd.concat([gender_diversity, nationality_diversity], axis=1)
st.dataframe(diversity_df.style.format("{}"))

st.subheader("📈 Final Grouping Clustering Quality Metrics")
st.metric("Silhouette Score (Higher is Better)", f"{sil_score_final:.3f}")
st.metric("Davies-Bouldin Index (Lower is Better)", f"{db_score_final:.3f}")

st.subheader("📤 Export Full Group Members")
export_df = groups_df[['Group', 'first_name', 'last_name', 'gender', 'nationality',
                       'hard_skills', 'soft_skills', 'creativity', 'teamwork']]
export_df = export_df.sort_values(by='Group')
st.dataframe(export_df)
csv_data = export_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Groups CSV", csv_data,
                   file_name=f"grouped_students_{selected_class}.csv", mime='text/csv')

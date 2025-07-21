import streamlit as st
import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
import random

st.set_page_config(layout="wide")
st.title("🤖 Group Formation: GMM + Genetic Algorithm Optimization")

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
num_students = len(class_df)

MIN_GROUP_SIZE = 5
MAX_GROUP_SIZE = 7
num_groups = int(np.ceil(num_students / MIN_GROUP_SIZE))

# Scale skills
scaler = MinMaxScaler()
scaled_skills = scaler.fit_transform(class_df[skill_cols])

# Clustering with GMM
gmm = GaussianMixture(n_components=num_groups, random_state=42)
clusters = gmm.fit_predict(scaled_skills)
class_df['Cluster'] = clusters

# Clustering metrics
sil_score = silhouette_score(scaled_skills, clusters)
db_score = davies_bouldin_score(scaled_skills, clusters)

st.subheader("📌 Clustering Metrics (GMM clusters on skills)")
st.metric("Silhouette Score (Higher is Better)", f"{sil_score:.3f}")
st.metric("Davies-Bouldin Index (Lower is Better)", f"{db_score:.3f}")

# Prepare GA

# Check if student is strong (>3.5 in any skill)
class_df["Is_Strong"] = class_df[skill_cols].max(axis=1) > 3.5

# Helper: initial grouping heuristic (round robin from clusters)
cluster_dict = {c: class_df[class_df['Cluster'] == c].index.tolist() for c in range(num_groups)}
cluster_iters = {c: iter(members) for c, members in cluster_dict.items()}

def initial_groups():
    groups = [[] for _ in range(num_groups)]
    group_idx = 0
    done = False
    while not done:
        done = True
        for c in range(num_groups):
            try:
                student_idx = next(cluster_iters[c])
                groups[group_idx].append(student_idx)
                group_idx = (group_idx + 1) % num_groups
                done = False
            except StopIteration:
                pass
    return groups

def repair_groups(groups):
    # Flatten all assigned students
    all_assigned = [s for g in groups for s in g]
    counts = {s: all_assigned.count(s) for s in all_assigned}
    duplicates = [s for s, c in counts.items() if c > 1]
    missing = list(set(range(num_students)) - set(all_assigned))

    # Remove duplicates beyond first occurrence
    for d in duplicates:
        occurrences = 0
        for g in groups:
            if d in g:
                occurrences += 1
                if occurrences > 1:
                    g.remove(d)
    
    # Assign missing students to groups with space
    for m in missing:
        for g in groups:
            if len(g) < MAX_GROUP_SIZE:
                g.append(m)
                break

    # Fix groups smaller than min size by redistributing or merging
    small_groups = [g for g in groups if len(g) < MIN_GROUP_SIZE]
    valid_groups = [g for g in groups if len(g) >= MIN_GROUP_SIZE]

    for sg in small_groups:
        members = sg[:]
        for m in members:
            for vg in valid_groups:
                if len(vg) < MAX_GROUP_SIZE:
                    vg.append(m)
                    sg.remove(m)
                    break

    groups = [g for g in groups if len(g) > 0]

    # Merge remaining small groups if any
    while True:
        small_groups = [g for g in groups if len(g) < MIN_GROUP_SIZE]
        if len(small_groups) < 2:
            break
        g1 = small_groups[0]
        g2 = small_groups[1]
        groups.remove(g1)
        groups.remove(g2)
        groups.append(g1 + g2)

    return groups

def fitness(groups):
    alpha, beta, gamma, delta = 2.0, 0.5, 1.0, 5.0
    scores = []
    for g in groups:
        if len(g) < MIN_GROUP_SIZE or len(g) > MAX_GROUP_SIZE:
            return -1000  # Strong penalty
        # Skill coverage
        group_skills = scaled_skills[g]
        skill_mean = np.mean(group_skills)
        skill_std = np.std(group_skills)
        # Want groups to have balanced skills => high mean, low std
        skill_score = alpha * skill_mean - beta * skill_std

        # Diversity: count unique genders and nationalities
        genders = class_df.loc[g, "gender"].nunique()
        nationalities = class_df.loc[g, "nationality"].nunique()
        diversity_score = gamma * (genders + nationalities)

        # At least one strong student per group
        has_strong = any(class_df.loc[g, "Is_Strong"])
        strong_score = delta if has_strong else -delta * 2  # heavy penalty if no strong student

        total = skill_score + diversity_score + strong_score
        scores.append(total)
    return np.mean(scores)

def crossover(p1, p2):
    cut = random.randint(1, len(p1) - 1)
    child = p1[:cut] + p2[cut:]
    return repair_groups(child)

def mutate(groups):
    # Swap random members between two groups
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
    return repair_groups(groups)

# Initialize population
POP_SIZE = 30
GENS = 100

population = []
for _ in range(POP_SIZE):
    ind = initial_groups()
    ind = repair_groups(ind)
    population.append(ind)

best_fitness = -np.inf
best_solution = None

progress_bar = st.progress(0)
fitness_values = []

for gen in range(GENS):
    population.sort(key=fitness, reverse=True)
    if fitness(population[0]) > best_fitness:
        best_fitness = fitness(population[0])
        best_solution = population[0]
    fitness_values.append(fitness(population[0]))
    
    # Selection: top 50%
    survivors = population[:POP_SIZE // 2]
    children = []
    while len(children) + len(survivors) < POP_SIZE:
        p1, p2 = random.sample(survivors, 2)
        child = crossover(p1, p2)
        if random.random() < 0.3:  # mutation chance
            child = mutate(child)
        children.append(child)
    population = survivors + children
    progress_bar.progress((gen+1)/GENS)

st.success(f"GA finished! Best fitness: {best_fitness:.3f}")

# Build final dataframe for best solution
final_rows = []
for gid, g in enumerate(best_solution, start=1):
    for idx in g:
        row = class_df.loc[idx].copy()
        row["Group"] = f"Group {gid}"
        final_rows.append(row)
final_df = pd.DataFrame(final_rows)

st.subheader("🧑‍🤝‍🧑 Optimized Groups")
st.dataframe(final_df[["Group", "Name", "gender", "nationality", "Cluster", *skill_cols]])

# Group size
group_sizes = final_df.groupby("Group").size()
st.subheader("📏 Group Sizes")
st.dataframe(group_sizes.rename("Size"))

# Skill variance
skill_var = final_df.groupby("Group")[skill_cols].var()
st.subheader("⚖️ Skill Variance per Group")
st.dataframe(skill_var.style.format("{:.3f}"))

# Demographic diversity
gender_div = final_df.groupby("Group")["gender"].nunique()
nat_div = final_df.groupby("Group")["nationality"].nunique()
diversity_df = pd.DataFrame({"Gender Diversity": gender_div, "Nationality Diversity": nat_div})
st.subheader("🌍 Demographic Diversity per Group")
st.dataframe(diversity_df)

# Show clustering metrics again for reference
st.subheader("📌 Clustering Metrics (GMM clusters on skills)")
st.metric("Silhouette Score (Higher is Better)", f"{sil_score:.3f}")
st.metric("Davies-Bouldin Index (Lower is Better)", f"{db_score:.3f}")

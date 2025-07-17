import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide")
st.title("🧠 Optimizing Balanced Student Group Formation")

CSV_PATH = "/workspaces/Stage/Datasets/students_train.csv"

# --- Load the data ---
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

required_cols = {"first_name", "last_name", "hard_skills", "soft_skills", "creativity", "teamwork", "class"}
if not required_cols.issubset(df.columns):
    st.error(f"The CSV must contain the columns: {required_cols}")
    st.stop()

# --- Class selection ---
unique_classes = sorted(df["class"].unique())
selected_class = st.selectbox("🎓 Select a class to group students from:", unique_classes)

# Filter students from the selected class
filtered_df = df[df["class"] == selected_class].reset_index(drop=True)

if filtered_df.empty:
    st.warning("No students found for the selected class.")
    st.stop()

st.subheader(f"📊 Students from class {selected_class}")
filtered_df["Name"] = filtered_df["first_name"] + " " + filtered_df["last_name"]
st.dataframe(filtered_df[["Name", "hard_skills", "soft_skills", "creativity", "teamwork"]])

# --- Feature normalization ---
features_raw = filtered_df[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].values
scaler = StandardScaler()
features = scaler.fit_transform(features_raw)

# --- Group settings ---
group_size = st.slider("🎯 Target group size", min_value=2, max_value=10, value=5, step=1)
num_students = len(filtered_df)
num_groups = int(np.ceil(num_students / group_size))
st.write(f"Total students: {num_students}, forming approximately {num_groups} heterogeneous groups")

# --- Initialize groups ---
groups_features = [np.empty((0, features.shape[1])) for _ in range(num_groups)]
groups_indices = [[] for _ in range(num_groups)]
unassigned_indices = list(range(num_students))

# --- Function to calculate variance
def calc_total_variance(groups):
    total_var = 0
    for g in groups:
        if g.shape[0] > 1:
            total_var += np.mean(np.std(g, axis=0))
    return total_var

# --- Greedy assignment (heterogeneous grouping)
while unassigned_indices:
    idx = unassigned_indices.pop(0)
    best_group = None
    best_variance = float('inf')

    for g_i in range(num_groups):
        temp_group = np.vstack([groups_features[g_i], features[idx].reshape(1, -1)])
        temp_groups = groups_features.copy()
        temp_groups[g_i] = temp_group
        variance = calc_total_variance(temp_groups)
        if variance < best_variance:
            best_variance = variance
            best_group = g_i

    # Fallback in case no best group is found (shouldn't happen)
    if best_group is None:
        best_group = min(range(num_groups), key=lambda i: len(groups_indices[i]))

    groups_features[best_group] = np.vstack([groups_features[best_group], features[idx].reshape(1, -1)])
    groups_indices[best_group].append(idx)

# --- Display group results ---
group_rows = []
for g_id, indices in enumerate(groups_indices, start=1):
    for idx in indices:
        row = filtered_df.iloc[idx].to_dict()
        row['Group'] = g_id
        row['Name'] = f"{row['first_name']} {row['last_name']}"
        group_rows.append(row)

groups_df = pd.DataFrame(group_rows)

def highlight_group(val):
    colors = ['#FFCDD2', '#C8E6C9', '#BBDEFB', '#FFF9C4', '#D1C4E9', '#B2DFDB', '#F8BBD0', '#DCEDC8', '#FFE0B2', '#CFD8DC']
    return f'background-color: {colors[(val-1) % len(colors)]}' if pd.notnull(val) else ''

st.subheader(f"📋 Heterogeneous Groups for class {selected_class}")
st.dataframe(groups_df[['Group', 'Name', 'hard_skills', 'soft_skills', 'creativity', 'teamwork']].style.applymap(highlight_group, subset=['Group']))

# --- Group Averages ---
st.subheader("📊 Average skill per group")
group_stats = groups_df.groupby('Group')[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].mean()
st.dataframe(group_stats.style.format("{:.2f}"))

# --- Group Standard Deviations ---
st.subheader("⚖️ Standard deviation per group (balance indicator)")
group_std = groups_df.groupby('Group')[['hard_skills', 'soft_skills', 'creativity', 'teamwork']].std()
group_std['Avg Std'] = group_std.mean(axis=1)
st.dataframe(group_std[['Avg Std']].style.format("{:.3f}"))

# --- Export CSV ---
export_df = pd.DataFrame([
    [filtered_df.iloc[idx]["first_name"] + " " + filtered_df.iloc[idx]["last_name"] for idx in indices]
    for indices in groups_indices
], columns=[f'Student {i+1}' for i in range(max(len(g) for g in groups_indices))])

csv_data = export_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download groups as CSV", csv_data, f"groups_{selected_class}.csv", "text/csv")

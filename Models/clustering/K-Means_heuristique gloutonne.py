import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide")
st.title("🧠 Optimisation de la formation des groupes équilibrés")

CSV_PATH = "/workspaces/Stage/Models/clustering/synthetic_students.csv"

# --- Chargement des données ---
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Erreur lors du chargement du CSV : {e}")
    st.stop()

required_cols = {"Name", "Hard Skills", "Soft Skills", "Creativity", "Teamwork"}
if not required_cols.issubset(df.columns):
    st.error(f"Le fichier CSV doit contenir les colonnes: {required_cols}")
    st.stop()

st.subheader("📊 Données étudiantes")
st.dataframe(df)

# --- Normalisation des données ---
features_raw = df[['Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']].values
scaler = StandardScaler()
features = scaler.fit_transform(features_raw)

# --- Paramètres de formation des groupes ---
group_size = st.slider("Taille des groupes", min_value=2, max_value=10, value=5, step=1)
num_students = len(df)
num_groups = num_students // group_size
st.write(f"Nombre total d'étudiants: {num_students}, Formation de {num_groups} groupes de {group_size}")

# --- Initialisation des groupes ---
groups_features = [np.empty((0, features.shape[1])) for _ in range(num_groups)]
groups_indices = [[] for _ in range(num_groups)]

# --- Algorithme glouton pour minimiser l'écart-type dans chaque groupe ---

# Liste des indices non assignés
unassigned_indices = list(range(num_students))

# Fonction calculant la variance moyenne pondérée par groupe
def calc_total_variance(groups):
    total_var = 0
    for g in groups:
        if g.shape[0] > 1:
            total_var += np.mean(np.std(g, axis=0))
    return total_var

# Assignation progressive
while unassigned_indices:
    idx = unassigned_indices.pop(0)
    best_group = None
    best_variance = float('inf')

    for g_i in range(num_groups):
        if len(groups_indices[g_i]) < group_size:
            # Simuler ajout
            temp_group = np.vstack([groups_features[g_i], features[idx].reshape(1, -1)])
            temp_groups = groups_features.copy()
            temp_groups[g_i] = temp_group
            variance = calc_total_variance(temp_groups)
            if variance < best_variance:
                best_variance = variance
                best_group = g_i

    # Ajout réel dans le meilleur groupe
    groups_features[best_group] = np.vstack([groups_features[best_group], features[idx].reshape(1, -1)])
    groups_indices[best_group].append(idx)

# --- Affichage des groupes formés ---
group_rows = []
for g_id, indices in enumerate(groups_indices, start=1):
    for idx in indices:
        row = df.iloc[idx].to_dict()
        row['Group'] = g_id
        group_rows.append(row)

groups_df = pd.DataFrame(group_rows)

def highlight_group(val):
    colors = ['#FFCDD2', '#C8E6C9', '#BBDEFB', '#FFF9C4', '#D1C4E9', '#B2DFDB', '#F8BBD0', '#DCEDC8', '#FFE0B2', '#CFD8DC']
    return f'background-color: {colors[(val-1) % len(colors)]}' if pd.notnull(val) else ''

st.subheader(f"📋 Groupes équilibrés ({group_size} étudiants par groupe)")
st.dataframe(groups_df[['Group', 'Name', 'Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']].style.applymap(highlight_group, subset=['Group']))

# --- Statistiques par groupe ---
st.subheader("📊 Moyennes des compétences par groupe")
group_stats = groups_df.groupby('Group')[['Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']].mean()
st.dataframe(group_stats.style.format("{:.2f}"))

st.subheader("⚖️ Écart-type moyen par groupe (indicateur d'équilibre)")
group_std = groups_df.groupby('Group')[['Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']].std()
group_std['Avg Std'] = group_std.mean(axis=1)
st.dataframe(group_std[['Avg Std']].style.format("{:.3f}"))

# --- Export CSV ---
export_df = pd.DataFrame([
    [df.iloc[idx]['Name'] for idx in indices] for indices in groups_indices
], columns=[f'Étudiant {i+1}' for i in range(group_size)])

csv_data = export_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Télécharger les groupes au format CSV", csv_data, "groupes_equilibres.csv", "text/csv")

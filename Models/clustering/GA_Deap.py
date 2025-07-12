import streamlit as st
import pandas as pd
import random
import numpy as np
from deap import base, creator, tools, algorithms

# --- UI Setup ---
st.set_page_config(layout="wide")
st.title("🧬 Optimisation de la formation de groupes (Algorithme Génétique)")

# --- Chargement CSV ---
CSV_PATH = "/workspaces/Stage/Models/clustering/synthetic_students.csv"

try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"Error : {e}")
    st.stop()

required_cols = {"Name", "Hard Skills", "Soft Skills", "Creativity", "Teamwork"}
if not required_cols.issubset(df.columns):
    st.error(f"required col: {required_cols}")
    st.stop()

st.subheader("📊 Student data")
st.dataframe(df)

# --- Paramètres ---
GROUP_SIZE = st.slider("Group size", 2, 10, 5)
num_students = len(df)
NUM_GROUPS = num_students // GROUP_SIZE

if num_students % GROUP_SIZE != 0:
    st.warning(f"{num_students} student can't be perfectly devided into equal groups {GROUP_SIZE}. these are excluded.")

student_ids = list(df.index)

# --- Fonction Fitness ---
def evaluate(individual):
    groups = [individual[i:i+GROUP_SIZE] for i in range(0, len(individual), GROUP_SIZE)]
    score = 0
    for group in groups:
        if len(group) < GROUP_SIZE:
            continue  # ignore incomplete groups
        scores = df.loc[group, ['Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']]
        diversity = scores.std().mean()  # Moyenne des écart-types par groupe
        score += diversity
    return score,

# --- Lancer l'optimisation ---
if st.button("🚀 Launch the optimisation GA"):

    try:
        # Protection contre redéfinition DEAP
        if "FitnessMax" not in creator.__dict__:
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if "Individual" not in creator.__dict__:
            creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register("indices", random.sample, student_ids, len(student_ids))
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=3)

        pop = toolbox.population(n=50)
        hof = tools.HallOfFame(1)

        # Lancement de l'algorithme génétique
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=100, halloffame=hof, verbose=False)

        best_ind = hof[0]
        st.success("✅ Optimisation done !")

        # --- Construction des groupes ---
        groups = [best_ind[i:i+GROUP_SIZE] for i in range(0, len(best_ind), GROUP_SIZE)]

        group_rows = []
        for g_id, group in enumerate(groups, start=1):
            if len(group) < GROUP_SIZE:
                continue  # Ignore les groupes incomplets
            for idx in group:
                row = df.loc[idx].to_dict()
                row['Group'] = g_id
                group_rows.append(row)

        groups_df = pd.DataFrame(group_rows)

        # --- Affichage des groupes ---
        st.subheader("👥 Groupes formés")
        def highlight_group(val):
            colors = ['#FFCDD2', '#C8E6C9', '#BBDEFB', '#FFF9C4', '#D1C4E9']
            return f'background-color: {colors[(val-1) % len(colors)]}' if pd.notnull(val) else ''

        st.dataframe(
            groups_df[['Group', 'Name', 'Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']]
            .style.applymap(highlight_group, subset=["Group"])
        )

        # --- Statistiques par groupe ---
        st.subheader("📊 Group skills Avg")
        group_stats = groups_df.groupby('Group')[['Hard Skills', 'Soft Skills', 'Creativity', 'Teamwork']].mean()
        st.dataframe(group_stats.style.format("{:.2f}"))

        # --- Export CSV ---
        export_df = pd.DataFrame([
            [df.loc[idx]['Name'] for idx in group]
            for group in groups if len(group) == GROUP_SIZE
        ], columns=[f'Étudiant {i+1}' for i in range(GROUP_SIZE)])

        csv_data = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Save groups  (CSV)", csv_data, "groupes_ga.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ Une erreur s'est produite : {e}")

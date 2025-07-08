import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Soft Skills Grouping", layout="wide")

st.title("🧑‍💻 Soft Skills Grouping & Clustering App")

st.markdown("""
Upload a CSV file with columns:  
- `student_id`, `communication_score`, `leadership_score`, `time_management_score`, `analytical_score`
""")

uploaded_file = st.file_uploader("Upload your students CSV", type=["csv"])

def create_soft_skills_balanced_groups(df, group_size=4, n_groups=25):
    soft_skills_features = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[soft_skills_features])
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    skill_clusters = kmeans.fit_predict(scaled_features)
    df_clustered = df.copy()
    df_clustered['skill_cluster'] = skill_clusters

    balanced_groups = []
    students_pool = df_clustered.copy()
    for group_id in range(n_groups):
        if len(students_pool) < group_size:
            break
        current_group = []
        for cluster_type in range(4):
            cluster_students = students_pool[students_pool['skill_cluster'] == cluster_type]
            if len(cluster_students) > 0 and len(current_group) < group_size:
                selected_student = cluster_students.sample(n=1).iloc[0]
                current_group.append(selected_student)
                students_pool = students_pool[students_pool.index != selected_student.name]
        while len(current_group) < group_size and len(students_pool) > 0:
            additional_student = students_pool.sample(n=1).iloc[0]
            current_group.append(additional_student)
            students_pool = students_pool[students_pool.index != additional_student.name]
        if len(current_group) > 0:
            balanced_groups.append(current_group)
    group_assignments = []
    for group_id, group_members in enumerate(balanced_groups):
        for member in group_members:
            assignment = {
                'student_id': member['student_id'],
                'group': group_id + 1,
                'skill_cluster': member['skill_cluster'],
                'communication_score': member['communication_score'],
                'leadership_score': member['leadership_score'],
                'time_management_score': member['time_management_score'],
                'analytical_score': member['analytical_score']
            }
            group_assignments.append(assignment)
    return pd.DataFrame(group_assignments), balanced_groups

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Preview of Uploaded Data", df.head())

    if st.button("Run Soft Skills Clustering"):
        assignments_df, groups = create_soft_skills_balanced_groups(df)

        st.success(f"Created {len(groups)} balanced groups!")
        st.write("### List of Students with Cluster Assignments")
        st.dataframe(assignments_df[['student_id', 'skill_cluster']].sort_values(['skill_cluster', 'student_id']).reset_index(drop=True))

        st.write("### Group Assignments", assignments_df.head(20))


        # Visualize all soft skills distributions by cluster
        st.write("### Soft Skills Distribution by Cluster")
        soft_skills = ['communication_score', 'leadership_score', 'time_management_score', 'analytical_score']
        fig, axs = plt.subplots(2, 2, figsize=(16, 10))
        axs = axs.flatten()
        for idx, skill in enumerate(soft_skills):
            ax = axs[idx]
            for cluster in sorted(assignments_df['skill_cluster'].unique()):
                cluster_data = assignments_df[assignments_df['skill_cluster'] == cluster]
                ax.hist(cluster_data[skill], alpha=0.5, label=f'Cluster {cluster} - {skill.replace("_score", "").title()}')
            ax.set_xlabel("Score")
            ax.set_ylabel("Count")
            ax.set_title(f"{skill.replace('_score', '').title()} by Cluster")
            ax.legend()
        plt.tight_layout()
        st.pyplot(fig)

        st.write("### Download Group Assignments")
        st.download_button(
            label="Download as CSV",
            data=assignments_df.to_csv(index=False),
            file_name="soft_skills_group_assignments.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload a CSV file to get started.")
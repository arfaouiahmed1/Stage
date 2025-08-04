# Student Clustering API: Research Article Draft

This repository contains the code and documentation for a research article on "Using Machine Learning Algorithms for Heterogeneous Student Group Formation". It includes both a Streamlit web application and a FastAPI backend implementation.

## Directory Structure

- `student_groups_api.py` - FastAPI implementation for student clustering and group formation
- `streamlit_app.py` - Interactive web application for student clustering
- `environment.yml` - Conda environment specification
- `article/` - Research article draft materials
- `data/` - Sample student datasets

## Getting Started

### Setup Environment

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate student-groups-api
```

### Run FastAPI Application

```bash
# Start the FastAPI server
uvicorn student_groups_api:app --reload
```

Access the API documentation at: http://127.0.0.1:8000/docs

### Run Streamlit Application

```bash
# Start the Streamlit application
streamlit run streamlit_app.py
```

## API Endpoints

- `GET /`: API documentation and status
- `POST /load-students/`: Load student data from CSV or JSON
- `POST /cluster/`: Perform clustering on student data
- `POST /form-groups/`: Create heterogeneous student groups
- `GET /visualize-clusters/`: Get PCA visualization of clusters

## Citation

If you use this code in your research, please cite:

```
@article{student_clustering_2023,
  title={Using Machine Learning Algorithms for Heterogeneous Student Group Formation},
  author={Your Name},
  journal={Journal Name},
  year={2023}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

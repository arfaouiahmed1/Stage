cd "c:\Users\ahmed\Desktop\Stage Esprit\Stage\Deployments\Backend"

conda activate ./.conda

python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
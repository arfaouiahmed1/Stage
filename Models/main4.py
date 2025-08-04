from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
from clustering2 import find_best_clustering, create_fixed_size_heterogeneous_groups

app = FastAPI()

@app.post("/cluster", response_class=JSONResponse)
async def cluster(
    request: Request,
    file: UploadFile = File(...),
    group_size: int = Form(...)
):
    # Load the uploaded CSV file into a pandas DataFrame
    df = pd.read_csv(file.file)

    # Perform clustering
    best_algo, best_score, best_result = find_best_clustering(df, k=4, metric='euclidean')

    # If no result was returned, return error JSON
    if best_result is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No suitable clustering found."}
        )

    clustered_df, labels, _ = best_result

    # Create fixed-size heterogeneous groups based on clustering
    grouped_df, group_counts = create_fixed_size_heterogeneous_groups(clustered_df, group_size=group_size)

    # Convert groups into a JSON-serializable dictionary
    groups = {
        str(group_id): group.to_dict(orient='records')
        for group_id, group in grouped_df.groupby('heterogeneous_group')
    }

    return {
        "algorithm": best_algo,
        "silhouette_score": round(best_score, 3),
        "group_size": group_size,
        "total_groups": len(groups),
        "group_counts": group_counts,
        "groups": groups
    }

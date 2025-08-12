from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
from ..schemas.group import (
    Group, 
    ClusteringRequest, 
    ClusteringResponse, 
    ClusteringConfig,
    GeneratedGroup,
    StudentMember
)
from ..core.firebase import db
from ..core.clustering_service import ClusteringService

router = APIRouter()
collection_name = "groups"

# Initialize clustering service (singleton pattern)
clustering_service = None

def get_clustering_service():
    global clustering_service
    if clustering_service is None:
        clustering_service = ClusteringService()
    return clustering_service

def doc_to_group(doc):
    data = doc.to_dict()
    return Group(
        idGroup=doc.id,
        groupName=data.get("groupName"),
        members=data.get("members", [])
    )

@router.post("/", response_model=Group)
def create_group(group: Group):
    """Create a new group"""
    doc_ref = db.collection(collection_name).document()
    data = group.dict(exclude={"idGroup"})
    doc_ref.set(data)
    return Group(idGroup=doc_ref.id, **data)

@router.get("/", response_model=List[Group])
def get_groups():
    """Get all groups"""
    docs = db.collection(collection_name).stream()
    return [doc_to_group(doc) for doc in docs]

@router.get("/{group_id}", response_model=Group)
def get_group(group_id: str):
    """Get a specific group by ID"""
    doc = db.collection(collection_name).document(group_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Group not found")
    return doc_to_group(doc)

@router.put("/{group_id}", response_model=Group)
def update_group(group_id: str, group: Group):
    """Update a group"""
    doc_ref = db.collection(collection_name).document(group_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Group not found")
    
    data = group.dict(exclude={"idGroup"})
    doc_ref.update(data)
    return Group(idGroup=group_id, **data)

@router.delete("/{group_id}")
def delete_group(group_id: str):
    """Delete a group"""
    doc_ref = db.collection(collection_name).document(group_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Group not found")
    
    doc_ref.delete()
    return {"message": "Group deleted successfully"}

@router.get("/search/", response_model=List[Group])
def search_groups(keyword: str):
    """Search groups by name"""
    docs = db.collection(collection_name).where("groupName", ">=", keyword).where("groupName", "<=", keyword + "\uf8ff").stream()
    return [doc_to_group(doc) for doc in docs]

# ===============================================
# CLUSTERING ENDPOINTS
# ===============================================

@router.post("/generate-clusters", response_model=ClusteringResponse)
async def generate_clusters(
    file: UploadFile = File(..., description="CSV file containing student data"),
    save_to_firebase: bool = True,
    group_name_prefix: str = "AI Generated Group"
):
    """
    Generate optimal student groups using optimized clustering algorithms with Firebase validation.
    
    **NEW FEATURES:**
    - **Real User Validation**: Automatically fetches Firebase user data to validate clustering
    - **CPU Optimized**: Uses MiniBatchKMeans and optimized algorithms for better performance
    - **Data Distribution Analysis**: Compares training data vs real user data
    - **Mixed Dataset Support**: Combines CSV training data with real Firebase users when available
    
    **Parameters:**
    - **file**: CSV file containing student data
    - **save_to_firebase**: Whether to save generated groups to Firebase (default: True)
    - **group_name_prefix**: Prefix for group names when saving (default: "AI Generated Group")
    
    **Expected CSV columns:**
    - first_name, last_name
    - hard_skills, soft_skills, creativity, teamwork
    - class, gender, nationality, age
    
    **Returns:**
    - best_algorithm: The algorithm that performed best
    - groups: List of generated groups with student details
    - validation_results: Data distribution analysis between CSV and Firebase data
    - data_source: Whether using "csv_only", "mixed", or "csv_with_validation"
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Get clustering service and generate groups with Firebase validation
        service = get_clustering_service()
        result = await service.generate_groups_with_firebase_validation(file)
        
        # Convert result to response format
        groups = []
        for group_data in result["groups"]:
            members = []
            for member_data in group_data["members"]:
                # Handle the 'class' field which might be named differently
                class_name = member_data.get("class", member_data.get("class_name", ""))
                
                # Handle gender mapping back to readable format
                gender_display = "Male" if member_data["gender"] == "M" else "Female" if member_data["gender"] == "F" else member_data["gender"]
                
                member = StudentMember(
                    first_name=member_data["first_name"],
                    last_name=member_data["last_name"],
                    hard_skills=float(member_data["hard_skills"]),
                    soft_skills=float(member_data["soft_skills"]),
                    creativity=float(member_data["creativity"]),
                    teamwork=float(member_data["teamwork"]),
                    class_name=class_name,
                    gender=gender_display,
                    nationality=member_data["nationality"],
                    age=int(member_data["age"])
                )
                members.append(member)
            
            group = GeneratedGroup(
                group=group_data["group"],
                size=group_data["size"],
                members=members
            )
            groups.append(group)
        
        # Save groups to Firebase if requested
        if save_to_firebase:
            print("Saving generated groups to Firebase...")
            for i, group_data in enumerate(result["groups"]):
                # Create member names list for Firebase Group schema with validation
                member_names = []
                for member in group_data["members"]:
                    first_name = member.get('first_name', '').strip()
                    last_name = member.get('last_name', '').strip()
                    
                    # Clean up corrupted names - remove random numbers and underscores
                    import re
                    first_name = re.sub(r'_\d+$', '', first_name)  # Remove trailing _numbers
                    last_name = re.sub(r'^_\d+\s*', '', last_name)  # Remove leading _numbers
                    
                    # Skip if names are clearly corrupted (like User_12345678)
                    if not (first_name.startswith('User_') and first_name.count('_') > 0):
                        full_name = f"{first_name} {last_name}".strip()
                        if len(full_name) > 1 and not full_name.startswith('_'):
                            member_names.append(full_name)
                        else:
                            # Use fallback if name is corrupted
                            member_names.append(f"Student {len(member_names) + 1}")
                    else:
                        # Use fallback for clearly corrupted User_ names
                        member_names.append(f"Student {len(member_names) + 1}")
                
                # Create Group object using existing schema
                firebase_group = Group(
                    groupName=f"{group_name_prefix} {i + 1}",
                    members=member_names
                )
                
                # Save to Firebase
                doc_ref = db.collection(collection_name).document()
                doc_ref.set(firebase_group.dict(exclude={"idGroup"}))
                print(f"Saved group {i + 1} with {len(member_names)} members: {member_names}")
        
        # Include validation metadata in response
        response = ClusteringResponse(
            best_algorithm=result["best_algorithm"],
            groups=groups
        )
        
        # Add validation info to response if available
        if 'validation_results' in result:
            print(f"Data Validation Summary:")
            print(f"- Data Source: {result.get('data_source', 'unknown')}")
            print(f"- Firebase Users: {result.get('firebase_users_count', 0)}")
            print(f"- CSV Users: {result.get('csv_users_count', 0)}")
            if result['validation_results'].get('distribution_warnings'):
                print(f"- Distribution Warnings: {len(result['validation_results']['distribution_warnings'])}")
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

@router.post("/generate-clusters-with-config", response_model=ClusteringResponse)
async def generate_clusters_with_config(
    file: UploadFile = File(..., description="CSV file containing student data"),
    group_size_min: int = 5,
    group_size_max: int = 7,
    population_size: int = 30,
    generations: int = 50,
    distance_metric: str = "euclidean",
    save_to_firebase: bool = True,
    group_name_prefix: str = "Custom AI Group"
):
    """
    Generate optimal student groups with custom configuration parameters.
    
    This endpoint allows you to customize the clustering parameters:
    - **group_size_min**: Minimum group size (default: 5)
    - **group_size_max**: Maximum group size (default: 7)
    - **population_size**: Genetic algorithm population size (default: 30)
    - **generations**: Number of genetic algorithm generations (default: 50)
    - **distance_metric**: Distance metric for clustering (default: "euclidean")
    - **save_to_firebase**: Whether to save generated groups to Firebase (default: True)
    - **group_name_prefix**: Prefix for group names when saving (default: "Custom AI Group")
    
    Expected CSV columns:
    - first_name, last_name, hard_skills, soft_skills, creativity, teamwork
    - class, gender, nationality, age
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Create config from parameters
        config = ClusteringConfig(
            group_size_min=group_size_min,
            group_size_max=group_size_max,
            population_size=population_size,
            generations=generations,
            distance_metric=distance_metric
        )
        
        # Get clustering service
        service = get_clustering_service()
        
        # Generate groups with custom configuration
        result = await service.generate_groups_with_config(
            file, 
            group_size_min=config.group_size_min,
            group_size_max=config.group_size_max,
            population_size=config.population_size,
            generations=config.generations,
            distance_metric=config.distance_metric
        )
        
        # Convert result to response format (same as above)
        groups = []
        for group_data in result["groups"]:
            members = []
            for member_data in group_data["members"]:
                class_name = member_data.get("class", member_data.get("class_name", ""))
                
                # Handle gender mapping back to readable format
                gender_display = "Male" if member_data["gender"] == "M" else "Female" if member_data["gender"] == "F" else member_data["gender"]
                
                member = StudentMember(
                    first_name=member_data["first_name"],
                    last_name=member_data["last_name"],
                    hard_skills=float(member_data["hard_skills"]),
                    soft_skills=float(member_data["soft_skills"]),
                    creativity=float(member_data["creativity"]),
                    teamwork=float(member_data["teamwork"]),
                    class_name=class_name,
                    gender=gender_display,
                    nationality=member_data["nationality"],
                    age=int(member_data["age"])
                )
                members.append(member)
            
            group = GeneratedGroup(
                group=group_data["group"],
                size=group_data["size"],
                members=members
            )
            groups.append(group)
        
        # Save groups to Firebase if requested
        if save_to_firebase:
            print("Saving generated groups to Firebase...")
            for i, group_data in enumerate(result["groups"]):
                # Create member names list for Firebase Group schema
                member_names = [f"{member['first_name']} {member['last_name']}" for member in group_data["members"]]
                
                # Create Group object using existing schema
                firebase_group = Group(
                    groupName=f"{group_name_prefix} {i + 1}",
                    members=member_names
                )
                
                # Save to Firebase
                doc_ref = db.collection(collection_name).document()
                doc_ref.set(firebase_group.dict(exclude={"idGroup"}))
                print(f"Saved group {i + 1} with {len(member_names)} members")
        
        return ClusteringResponse(
            best_algorithm=result["best_algorithm"],
            groups=groups
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

@router.post("/generate-clusters-quick", response_model=ClusteringResponse)
async def generate_clusters_quick(
    file: UploadFile = File(..., description="CSV file containing student data"),
    save_to_firebase: bool = True,
    group_name_prefix: str = "Quick AI Group"
):
    """
    Generate student groups using ultra-fast MiniBatch clustering (fastest option).
    
    **OPTIMIZED FOR SPEED:**
    - Uses only MiniBatchKMeans for maximum performance
    - Reduced iterations and simplified optimization
    - Ideal for large datasets (1000+ students)
    - 10-50x faster than full clustering pipeline
    
    **Parameters:**
    - **file**: CSV file containing student data
    - **save_to_firebase**: Whether to save generated groups to Firebase (default: True)
    - **group_name_prefix**: Prefix for group names when saving (default: "Quick AI Group")
    
    **Expected CSV columns:**
    - first_name, last_name
    - hard_skills, soft_skills, creativity, teamwork
    - class, gender, nationality, age
    
    **Returns:**
    - best_algorithm: "MiniBatch_KMeans_Fast"
    - groups: List of generated groups with student details
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Get clustering service and use ultra-fast generation
        service = get_clustering_service()
        result = await service.generate_groups_quick(file)
        
        # Convert result to response format (same as above)
        groups = []
        for group_data in result["groups"]:
            members = []
            for member_data in group_data["members"]:
                # Handle the 'class' field which might be named differently
                class_name = member_data.get("class", member_data.get("class_name", ""))
                
                # Handle gender mapping back to readable format
                gender_display = "Male" if member_data["gender"] == "M" else "Female" if member_data["gender"] == "F" else member_data["gender"]
                
                member = StudentMember(
                    first_name=member_data["first_name"],
                    last_name=member_data["last_name"],
                    hard_skills=float(member_data["hard_skills"]),
                    soft_skills=float(member_data["soft_skills"]),
                    creativity=float(member_data["creativity"]),
                    teamwork=float(member_data["teamwork"]),
                    class_name=class_name,
                    gender=gender_display,
                    nationality=member_data["nationality"],
                    age=int(member_data["age"])
                )
                members.append(member)
            
            group = GeneratedGroup(
                group=group_data["group"],
                size=group_data["size"],
                members=members
            )
            groups.append(group)
        
        # Save groups to Firebase if requested
        if save_to_firebase:
            print("Saving generated groups to Firebase...")
            for i, group_data in enumerate(result["groups"]):
                # Create member names list for Firebase Group schema
                member_names = [f"{member['first_name']} {member['last_name']}" for member in group_data["members"]]
                
                # Create Group object using existing schema
                firebase_group = Group(
                    groupName=f"{group_name_prefix} {i + 1}",
                    members=member_names
                )
                
                # Save to Firebase
                doc_ref = db.collection(collection_name).document()
                doc_ref.set(firebase_group.dict(exclude={"idGroup"}))
                print(f"Saved group {i + 1} with {len(member_names)} members")
        
        return ClusteringResponse(
            best_algorithm=result["best_algorithm"],
            groups=groups
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")
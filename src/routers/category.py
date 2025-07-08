from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.category import Category
from src.core.firebase import db  # ton client Firestore

router = APIRouter()
collection_name = "categories"

def doc_to_category(doc):
    data = doc.to_dict()
    return Category(
        idCategory=doc.id,
        island=data.get("island")
    )

@router.post("/", response_model=Category)
def create_category(category: Category):
    doc_ref = db.collection(collection_name).document()  # Firestore génère ID
    data = category.dict(exclude={"idCategory"})  # exclure idCategory si présent
    doc_ref.set(data)
    # Retourner avec l’ID généré
    return Category(idCategory=doc_ref.id, **data)


@router.get("/", response_model=List[Category])
def get_categories():
    docs = db.collection(collection_name).stream()
    return [doc_to_category(doc) for doc in docs]

@router.get("/{category_id}", response_model=Category)
def get_category(category_id: str):
    doc = db.collection(collection_name).document(category_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Category non trouvée")
    return doc_to_category(doc)

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: str, category: Category):
    doc_ref = db.collection(collection_name).document(category_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Category non trouvée")
    doc_ref.set(category.dict())
    return category

@router.delete("/{category_id}")
def delete_category(category_id: str):
    doc_ref = db.collection(collection_name).document(category_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Category non trouvée")
    doc_ref.delete()
    return {"detail": "Category supprimée"}

from fastapi import APIRouter, Form, HTTPException
from services.collection_service import (
    list_collections,
    create_collection,
    get_collection,
    delete_collection
)

router = APIRouter()

@router.get("")
def get_collections():
    return {"collections": list_collections()}

@router.post("")
def post_collection(name: str = Form(...)):
    try:
        create_collection(name)
        return {"status": "collection created", "collection": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{collection_id}")
def fetch_collection(collection_id: str):
    if not get_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"collection": collection_id}

@router.delete("/{collection_id}")
def remove_collection(collection_id: str):
    try:
        delete_collection(collection_id)
        return {"status": "collection deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

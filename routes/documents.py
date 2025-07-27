import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from services.document_service import (
    list_documents,
    upload_document,
    delete_document,
    semantic_search
)

router = APIRouter()

class SearchQuery(BaseModel):
    query: str

@router.get("")
def get_documents(collection_id: str):
    return {"documents": list_documents(collection_id)}

@router.post("")
async def post_document(collection_id: str, file: UploadFile = File(...)):
    try:
        doc_id = str(uuid.uuid4())
        chunks_added = await upload_document(collection_id, doc_id, file)
        return {"status": "success", "document_id": doc_id, "chunks_added": chunks_added}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
def remove_document(collection_id: str, document_id: str):
    try:
        delete_document(collection_id, document_id)
        return {"status": "document deleted", "document_id": document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
def post_search(collection_id: str, search: SearchQuery):
    try:
        results, prompt = semantic_search(collection_id, search.query)
        return {"results": results, "final_prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI
from routes import collections, documents

app = FastAPI(title="LangConnect-Compatible RAG API")

# Include routers
app.include_router(collections.router, prefix="/collections", tags=["Collections"])
app.include_router(documents.router, prefix="/collections/{collection_id}/documents", tags=["Documents"])

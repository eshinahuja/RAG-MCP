import os
import json
from typing import List, Tuple
from embedding import Embedder
from loader import load_and_chunk
from vector_store.FAISSStore import FAISSStore

TMP_DIR = "tmp"
META_FILE = "metadata.json"
CHUNK_SIZE = 500
OVERLAP = 50

embedder = Embedder()

def _get_metadata_path(collection_id: str) -> str:
    return os.path.join("data", collection_id, META_FILE)

def list_documents(collection_id: str) -> List[str]:
    path = _get_metadata_path(collection_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        meta = json.load(f)
    return list(meta.keys())

async def upload_document(collection_id: str, document_id: str, file) -> int:
    os.makedirs(TMP_DIR, exist_ok=True)
    tmp_path = os.path.join(TMP_DIR, file.filename)
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    chunks = load_and_chunk(tmp_path, CHUNK_SIZE, OVERLAP)
    embeddings = embedder.embed_texts(chunks)

    store = FAISSStore(collection_id)
    store.add(document_id, embeddings, chunks)

    os.remove(tmp_path)

    # Save metadata
    meta_path = _get_metadata_path(collection_id)
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
    else:
        meta = {}

    meta[document_id] = file.filename

    with open(meta_path, "w") as f:
        json.dump(meta, f)

    return len(chunks)

def delete_document(collection_id: str, document_id: str):
    store = FAISSStore(collection_id)
    store.delete(document_id)

    meta_path = _get_metadata_path(collection_id)
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
        if document_id in meta:
            del meta[document_id]
            with open(meta_path, "w") as f:
                json.dump(meta, f)

def semantic_search(collection_id: str, query: str) -> Tuple[List[str], str]:
    query_embedding = embedder.embed_texts([query])[0]
    store = FAISSStore(collection_id)
    results = store.search(query_embedding)
    composed_prompt = "\n".join([r["text"] for r in results]) + f"\n\nUser Query: {query}"
    return results, composed_prompt

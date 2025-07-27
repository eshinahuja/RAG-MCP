import os
import faiss
import numpy as np
import json
import shutil


class FAISSStore:
    def __init__(self, collection_id: str):
        self.collection_id = collection_id
        self.index_path = os.path.join("data", collection_id, "index.faiss")
        self.meta_path = os.path.join("data", collection_id, "vectors.json")
        self.index = self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        return faiss.IndexFlatL2(384)  # dimension must match your embedding model

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

    def _load_metadata(self):
        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata):
        with open(self.meta_path, "w") as f:
            json.dump(metadata, f)

    def add(self, document_id, embeddings, texts):
        metadata = self._load_metadata()
        base_id = len(metadata)
        for i, (vec, text) in enumerate(zip(embeddings, texts)):
            metadata[str(base_id + i)] = {"text": text, "document_id": document_id}
            self.index.add(np.array([vec], dtype=np.float32))
        self._save_metadata(metadata)
        self.save()

    def search(self, query_vec, top_k=5):
        metadata = self._load_metadata()
        D, I = self.index.search(np.array([query_vec], dtype=np.float32), top_k)
        results = []
        for idx in I[0]:
            meta = metadata.get(str(idx))
            if meta:
                results.append(meta)
        return results

    def delete(self, document_id):
        metadata = self._load_metadata()
        new_meta = {}
        vectors = []

        for idx, value in metadata.items():
            if value["document_id"] != document_id:
                new_meta[str(len(vectors))] = value
                vectors.append(self.index.reconstruct(int(idx)))

        self.index = faiss.IndexFlatL2(384)
        if vectors:
            self.index.add(np.array(vectors, dtype=np.float32))

        self._save_metadata(new_meta)
        self.save()

    @staticmethod
    def list_collections():
        path = "data"
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    @staticmethod
    def create_collection(name):
        os.makedirs(os.path.join("data", name), exist_ok=True)

    @staticmethod
    def delete_collection(name):
        shutil.rmtree(os.path.join("data", name), ignore_errors=True)

    @staticmethod
    def exists(name):
        return os.path.exists(os.path.join("data", name))

    def list_documents(self):
        meta = self._load_metadata()
        doc_ids = set(v["document_id"] for v in meta.values())
        return list(doc_ids)

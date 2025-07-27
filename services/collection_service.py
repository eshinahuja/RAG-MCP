import os
import shutil

BASE_PATH = "data"

def list_collections():
    if not os.path.exists(BASE_PATH):
        return []
    return [f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f))]

def create_collection(name: str):
    os.makedirs(os.path.join(BASE_PATH, name), exist_ok=True)

def get_collection(name: str):
    path = os.path.join(BASE_PATH, name)
    return os.path.exists(path)

def delete_collection(name: str):
    path = os.path.join(BASE_PATH, name)
    if os.path.exists(path):
        shutil.rmtree(path)

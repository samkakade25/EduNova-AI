import faiss
import os
import numpy as np
import pickle

INDEX_PATH = "models/faiss_index"

def save_faiss(index, texts):
    os.makedirs(INDEX_PATH, exist_ok=True)
    faiss.write_index(index, os.path.join(INDEX_PATH, "doc.index"))
    with open(os.path.join(INDEX_PATH, "texts.pkl"), "wb") as f:
        pickle.dump(texts, f)

def load_faiss():
    index = faiss.read_index(os.path.join(INDEX_PATH, "doc.index"))
    with open(os.path.join(INDEX_PATH, "texts.pkl"), "rb") as f:
        texts = pickle.load(f)
    return index, texts

def create_faiss_index(embeddings):
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index

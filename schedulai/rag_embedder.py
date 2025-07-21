import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

knowledge_dir = "data/knowledge_base"
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight, accurate


def load_knowledge():
    texts = []
    for fname in os.listdir(knowledge_dir):
        with open(os.path.join(knowledge_dir, fname), "r", encoding="utf-8") as f:
            texts.append(f.read())
    return texts


def embed_and_save():
    docs = load_knowledge()
    embeddings = embedding_model.encode(docs, show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    with open("faiss_index.pkl", "wb") as f:
        pickle.dump((index, docs), f)

    print("✅ FAISS index saved.")


if __name__ == "__main__":
    embed_and_save()

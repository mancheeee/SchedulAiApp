import faiss
import pickle
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_context(query, k=1):
    with open("faiss_index.pkl", "rb") as f:
        index, docs = pickle.load(f)

    query_vector = embedding_model.encode([query])
    distances, indices = index.search(query_vector, k)

    return "\n".join([docs[i] for i in indices[0]])

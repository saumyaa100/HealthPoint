import os
import numpy as np
from typing import List, Tuple
from app.utils.logger import get_logger
import app.config as cfg

logger = get_logger(__name__)

# Optional pinecone usage
USE_PINECONE = bool(cfg.PINECONE_API_KEY and cfg.PINECONE_ENV)

if USE_PINECONE:
    import pinecone
    pinecone.init(api_key=cfg.PINECONE_API_KEY, environment=cfg.PINECONE_ENV)
    # ensure index exists
    if cfg.PINECONE_INDEX not in pinecone.list_indexes():
        pinecone.create_index(cfg.PINECONE_INDEX, dimension=1536)  # embedding dim placeholder (OpenAI text-embedding-3-small is 1536)
    pinecone_index = pinecone.Index(cfg.PINECONE_INDEX)
else:
    pinecone_index = None

# We'll call OpenAI directly for embeddings (or Pinecone if configured)
import openai
openai.api_key = cfg.OPENAI_API_KEY

def _embed_text_openai(texts: List[str], model: str):
    """
    Call OpenAI embeddings API on list of texts. Returns list of numpy arrays.
    """
    logger.info(f"Embedding {len(texts)} chunks with model {model}")
    # OpenAI may accept up to 2048 at once; but to be safe, do in small batches
    embeds = []
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        resp = openai.embeddings.create(model=model, input=batch)
        for item in resp["data"]:
            vec = np.array(item["embedding"], dtype=np.float32)
            embeds.append(vec)
    return embeds

def vector_norm(v: np.ndarray) -> float:
    return np.linalg.norm(v) if np.linalg.norm(v) != 0 else 1e-12

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (vector_norm(a) * vector_norm(b)))

class InMemoryVectorStore:
    def __init__(self):
        self.ids = []
        self.vectors = []
        self.metadatas = []

    def upsert(self, ids: List[str], vectors: List[np.ndarray], metadatas: List[dict]):
        for i, vec in enumerate(vectors):
            self.ids.append(ids[i])
            self.vectors.append(vec)
            self.metadatas.append(metadatas[i])

    def query(self, query_vec: np.ndarray, top_k: int = 3) -> List[Tuple[dict, float]]:
        sims = []
        for meta_vec, meta in zip(self.vectors, self.metadatas):
            score = cosine_similarity(query_vec, meta_vec)
            sims.append((meta, score))
        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:top_k]

# Single in-memory store per process (no persistence)
_inmem_store = InMemoryVectorStore()

def build_embeddings_and_store(chunks: List[dict], embed_model: str):
    texts = [c["text"] for c in chunks]
    if len(texts) == 0:
        return []
    vectors = _embed_text_openai(texts, model=embed_model)
    ids = [str(c["id"]) for c in chunks]
    metadatas = [{"id": c["id"], "text": c["text"]} for c in chunks]

    if USE_PINECONE:
        # Upsert to pinecone index
        logger.info("Upserting embeddings to Pinecone")
        to_upsert = [(ids[i], vectors[i].tolist(), metadatas[i]) for i in range(len(ids))]
        pinecone_index.upsert(vectors=to_upsert)
    else:
        logger.info("Upserting embeddings to in-memory store")
        _inmem_store.upsert(ids, vectors, metadatas)
    return vectors

def query_top_k(query: str, embed_model: str, top_k: int = 3):
    """
    Embeds the query and returns top_k chunks as list of dicts with score.
    """
    q_vecs = _embed_text_openai([query], model=embed_model)
    q_vec = q_vecs[0]
    if USE_PINECONE:
        logger.info("Querying Pinecone for top_k")
        result = pinecone_index.query(vector=q_vec.tolist(), top_k=top_k, include_metadata=True)
        hits = []
        for match in result["matches"]:
            hits.append((match["metadata"], float(match["score"])))
        return hits
    else:
        logger.info("Querying in-memory store for top_k")
        hits = _inmem_store.query(q_vec, top_k=top_k)
        return hits

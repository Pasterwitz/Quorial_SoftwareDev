from __future__ import annotations
import os, json
import chromadb
from chromadb.utils import embedding_functions

def _sanitize_metadata(meta: dict | None) -> dict:

    if not isinstance(meta, dict):
        return {}
    out: dict = {}
    for k, v in meta.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            # fallback: stringify lists/dicts/objects
            try:
                out[k] = str(v)
            except Exception:
                continue
    return out

CHROMA_PATH = os.environ.get("CHROMA_PATH", "./voxeurop_db")
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "voxeurop_articles")
CHUNKED_JSON = os.environ.get("CHUNKED_JSON", "data/chunked/chunked_articles.json")


ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)
col = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
    embedding_function=ef,
)

with open(CHUNKED_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

# Expect items like: {"document": "...", "metadata": {"article_id": ..., "chunk_idx": ...}}
BATCH = 512
ids, docs, metas = [], [], []
for i, item in enumerate(data):
    doc = item.get("document") or ""
    if not isinstance(doc, str) or not doc.strip():
        continue  # skip empty docs
    ids.append(item.get("id") or f"chunk_{i}")
    docs.append(doc)
    metas.append(_sanitize_metadata(item.get("metadata", {})))

    if len(ids) == BATCH:
        col.add(ids=ids, documents=docs, metadatas=metas)
        ids, docs, metas = [], [], []

if ids:
    col.add(ids=ids, documents=docs, metadatas=metas)

print(f"Rebuilt Chroma collection successfully. Count = {col.count()}")
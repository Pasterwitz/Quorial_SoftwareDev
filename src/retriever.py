from __future__ import annotations
from typing import Any, Dict, List, Optional
import chromadb

from src.chroma_config import get_chroma_config

CONFIG = get_chroma_config()


def _get_collection() -> chromadb.api.models.Collection.Collection:
    """
    Connect to the existing persistent Chroma DB and open the target collection
    """
    client = chromadb.PersistentClient(path=CONFIG.path)
    collection = client.get_or_create_collection(
        name=CONFIG.collection,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def _to_results(res: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert Chroma query response to a flat list with id, text, metadata, and similarity
    """
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    ids = res.get("ids", [[]])[0]
    dists = res.get("distances", [[]])[0] or []

    sims = [1.0 - float(d) for d in dists] if dists else [None] * len(docs)

    out: List[Dict[str, Any]] = []
    for i in range(len(docs)):
        out.append({
            "id": ids[i],
            "text": docs[i],
            "metadata": metas[i] if metas and i < len(metas) else {},
            "score": sims[i],
        })
    return out


def chroma_retrieve(
    query: str,
    top_k: int = 10,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Semantic retrieval from Chroma
    """
    col = _get_collection()
    res = col.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    return _to_results(res)


# Parent expansion (surrounding chunks)
def _fetch_article_chunks(
    article_id: Any,
) -> List[Dict[str, Any]]:
    """
    Pull ALL chunks for an article_id from Chroma once, sort by chunk_idx
    """
    col = _get_collection()

    collected: List[Dict[str, Any]] = []
    page = 0
    page_size = 500
    while True:
        batch = col.get(
            where={"article_id": article_id},
            include=["documents", "metadatas"],
            limit=page_size,
            offset=page * page_size,
        )
        ids = batch.get("ids", [])
        if not ids:
            break
        docs = batch["documents"]
        metas = batch["metadatas"]
        for i in range(len(ids)):
            collected.append({
                "id": ids[i],
                "text": docs[i],
                "metadata": metas[i] if metas and i < len(metas) else {},
            })
        if len(ids) < page_size:
            break
        page += 1

    # Sort by chunk_idx if present
    def _ck(m: Dict[str, Any]) -> int:
        try:
            return int(m["metadata"].get("chunk_idx", 0))
        except Exception:
            return 0

    collected.sort(key=_ck)
    return collected


def _expand_around_primary(
    primary_hit: Dict[str, Any],
    context_size: int = 2,
) -> Optional[Dict[str, Any]]:
    """
    Build a combined context around the primary chunk using article_id & chunk_idx
    """
    meta = primary_hit.get("metadata", {}) or {}
    if "article_id" not in meta or "chunk_idx" not in meta:
        return None

    article_id = meta["article_id"]
    center_idx = int(meta["chunk_idx"])

    article_chunks = _fetch_article_chunks(article_id)
    if not article_chunks:
        return None

    # Build a window [center - context_size, center + context_size]
    start = max(0, center_idx - context_size)
    end = center_idx + context_size

    window: List[Dict[str, Any]] = []
    for ch in article_chunks:
        ck = int(ch["metadata"].get("chunk_idx", -1))
        if start <= ck <= end:
            window.append({
                "chunk_idx": ck,
                "article_id": article_id,
                "title": ch["metadata"].get("title"),
                "summary": ch["metadata"].get("summary"),
                "chunk_id": ch["id"],
                "content": ch["text"],
                "is_primary": (ck == center_idx),
            })

    if not window:
        return None

    window.sort(key=lambda x: x["chunk_idx"])
    combined = "\n\n".join(w["content"] for w in window)

    # Carry a score from the primary (if present)
    score = primary_hit.get("score", None)

    return {
        "primary_chunk_idx": center_idx,
        "article_id": article_id,
        "title": meta.get("title"),
        "summary": meta.get("summary"),
        "score": score,
        "combined_content": combined,
        "chunk_details": window,
        "total_chunks": len(window),
    }


# API
def retrieve(
    query: str,
    top_k: int = 5,
    context_size: int = 2,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Returns parent-expanded results
    """
    hits = chroma_retrieve(query, top_k=top_k, where=where)

    expanded: List[Dict[str, Any]] = []
    for hit in hits:
        exp = _expand_around_primary(hit, context_size=context_size)
        if exp:
            expanded.append(exp)

    return expanded


def print_retrieval_results(results: List[Dict[str, Any]], max_content_length: int = 200):
    """
    Pretty printer for quick checks
    """
    print("\n" + "=" * 80)
    print("RETRIEVAL RESULTS (Chroma)")
    print("=" * 80)

    for i, r in enumerate(results, 1):
        title = r.get("title") or "—"
        print(f"\n--- Result {i} ---")
        print(f"Article ID: {r['article_id']}  |  Title: {title}")
        print(f"Score: {r.get('score') if r.get('score') is not None else '—'}")
        print(f"Total chunks included: {r['total_chunks']}")
        preview = (r["combined_content"] or "")[:max_content_length].replace("\n", " ")
        print(f"Content preview: {preview}...")
        chunk_info = [f"#{c['chunk_idx']}{'*' if c['is_primary'] else ''}" for c in r["chunk_details"]]
        print(f"Chunks: {', '.join(chunk_info)} (* = primary match)")


# test
if __name__ == "__main__":
    test_queries = [
        "Bulgaria EU politics",
        "EU migration policy and border control",
        "Inflation trends in Germany",
    ]
    for q in test_queries:
        res = retrieve(q, top_k=5, context_size=2, where=None)
        print_retrieval_results(res, max_content_length=200)

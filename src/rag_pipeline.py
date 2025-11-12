from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
from openai import OpenAI

from src.retriever import retrieve

def _build_context(sources: List[Dict[str, Any]]) -> str:
    """
    Turn retrieved results into a single context string for the LLM.
    Each source is one article (with combined chunk window).
    """
    blocks: List[str] = []
    for i, src in enumerate(sources, start=1):
        title = src.get("title") or "Unknown title"
        article_id = src.get("article_id", "N/A")
        summary = src.get("summary") or ""
        header = f"[Source {i}] {title} (article_id={article_id})"
        if summary:
            header += f"\nSummary: {summary}"
        content = (src.get("combined_content") or "").strip()
        blocks.append(header + "\n\n" + content)
    return "\n\n---\n\n".join(blocks)


def generate_rag_response(
    query: str,
    sources: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:

    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No OpenAI API key provided. "
            "Pass api_key=... or set OPENAI_API_KEY env var."
        )

    client = OpenAI(api_key=api_key)

    context = _build_context(sources)

    system_prompt = (
        "You are a careful assistant answering questions about news articles. "
        "Use only the information in the provided CONTEXT. "
        "If the answer is not in the context, say that you do not know. "
        "Cite which sources you used (e.g. [Source 1], [Source 2]) in your answer."
    )

    user_prompt = (
        f"Question:\n{query}\n\n"
        f"CONTEXT:\n{context}\n\n"
        "Answer the question based only on the CONTEXT above. "
        "If something is unclear or missing, explicitly say that it is not covered."
    )

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = completion.choices[0].message.content

    source_infos = []
    for i, s in enumerate(sources, start=1):
        source_infos.append(
            {
                "source_index": i,
                "article_id": s.get("article_id"),
                "title": s.get("title"),
                "summary": s.get("summary"),
                "score": s.get("score"),
                "chunk_indices": [c["chunk_idx"] for c in s.get("chunk_details", [])],
            }
        )

    return {
        "query": query,
        "answer": answer,
        "sources": source_infos,
    }


def complete_rag_pipeline(
    query: str,
    api_key: Optional[str] = None,
    top_k: int = 10,
    context_window: int = 2,
    max_articles: int = 2,
    where: Optional[Dict[str, Any]] = None,
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """
    Full RAG pipeline:

      1) Retrieve top_k candidates from Chroma (each with windowed chunks)
      2) Take top `max_articles` as context
      3) Call the LLM once to generate an answer
    """
    # Step 1: retrieval
    hits = retrieve(
        query=query,
        top_k=top_k,
        context_size=context_window,
        where=where,
    )

    if not hits:
        return {
            "query": query,
            "answer": "I could not find any relevant articles in the collection.",
            "sources": [],
        }

    # Step 2: pick a subset of articles for the LLM context
    top_sources = hits[:max_articles]

    # Step 3: generate answer
    result = generate_rag_response(
        query=query,
        sources=top_sources,
        api_key=api_key,
        model=model,
    )
    return result


# test
if __name__ == "__main__":
    test_queries = [
        "What does Voxeurop report about Bulgaria and EU politics?",
        "What are the main points about EU migration policy at the external borders?",
    ]

    api_key = os.environ.get("OPENAI_API_KEY")

    for q in test_queries:
        print("\n" + "=" * 80)
        print("QUERY:", q)
        print("=" * 80)

        out = complete_rag_pipeline(
            query=q,
            api_key=api_key,
            top_k=10,
            context_window=2,
            max_articles=2,
            where=None,
        )

        print("\nANSWER:\n", out["answer"])
        print("\nSOURCES:")
        for s in out["sources"]:
            print(
                f"  [Source {s['source_index']}] {s.get('title')!r} "
                f"(article_id={s.get('article_id')}, score={s.get('score')})"
            )

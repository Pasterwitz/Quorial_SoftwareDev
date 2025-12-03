from __future__ import annotations
from typing import Any, Dict, List, Optional
import os

from dotenv import load_dotenv
from openai import OpenAI
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.retriever import retrieve

# Ensure variables from a local .env are available when running the pipeline directly.
load_dotenv()

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


def _call_openai_llm(system_prompt: str, user_prompt: str, model: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return completion.choices[0].message.content


def _call_mistral_llm(system_prompt: str, user_prompt: str, model: str, api_key: str) -> str:
    client = MistralClient(api_key=api_key)
    completion = client.chat(
        model=model,
        messages=[
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ],
        temperature=0.2,
    )

    content = completion.choices[0].message.content

    if isinstance(content, str):
        return content

    # Some SDK versions return structured chunks; join any text fields we find.
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
            elif isinstance(item, str):
                parts.append(item)
            else:
                nested = getattr(item, "content", None)
                if nested:
                    parts.append(str(nested))
        return "".join(parts).strip()

    return str(content)


def generate_rag_response(
    query: str,
    sources: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    provider: str = "openai",
) -> Dict[str, Any]:

    provider = provider.lower()
    if provider not in {"openai", "mistral"}:
        raise ValueError("provider must be either 'openai' or 'mistral'")

    if model is None:
        model = "mistral-small-latest" if provider == "mistral" else "gpt-4o-mini"

    if api_key is None:
        env_var = "MISTRAL_API_KEY" if provider == "mistral" else "OPENAI_API_KEY"
        api_key = os.environ.get(env_var)
    else:
        env_var = None

    if not api_key:
        env_note = env_var or ("MISTRAL_API_KEY" if provider == "mistral" else "OPENAI_API_KEY")
        raise RuntimeError(
            f"No {provider} API key provided. "
            f"Pass api_key=... or set {env_note} env var."
        )

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

    if provider == "mistral":
        answer = _call_mistral_llm(system_prompt, user_prompt, model, api_key)
    else:
        answer = _call_openai_llm(system_prompt, user_prompt, model, api_key)

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
    model: Optional[str] = None,
    provider: str = "openai",
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
        provider=provider,
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

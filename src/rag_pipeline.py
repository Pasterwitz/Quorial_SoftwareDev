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
        summary = src.get("summary") or ""
        # Do not expose internal article IDs in the context header; include title only
        header = f"[Source {i}] {title}"
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

    system_prompt = """
You are a careful assistant answering questions about news articles.

Use only the information in the provided context.
If the answer is not in the context, say that you do not know.

Structure every answer using the following format and bold section headers:

Summary
A short, coherent paragraph that captures the main answer based strictly on the CONTEXT.

Key Insights
• Bullet points presenting the essential facts from the CONTEXT.
• Keep them concise and avoid unnecessary wording.

Gaps in the Context
Clearly state which parts of the question cannot be answered because they are not covered in the CONTEXT.

Your answers should remain clear, concise, and logically structured.
"""


    user_prompt = f"""
Question:
{query}

CONTEXT:
{context}

Answer the question strictly based on the CONTEXT above.
If something is unclear, missing, or not supported by the CONTEXT, state this explicitly in the 'Gaps in the Context' section.
Follow the structure defined in the system prompt.
"""


    if provider == "mistral":
        answer = _call_mistral_llm(system_prompt, user_prompt, model, api_key)
    else:
        answer = _call_openai_llm(system_prompt, user_prompt, model, api_key)

    source_infos = []
    for i, s in enumerate(sources, start=1):
        # Return only the title and relevance score (no internal article_id),
        # format the score as a percentage string for display purposes,
        # and ensure chunk indices are available for debugging if needed.
        raw_score = s.get("score")
        pct_score = None
        try:
            if raw_score is not None:
                pct_score = f"{float(raw_score) * 100:.1f}%"
        except Exception:
            pct_score = str(raw_score)

        source_infos.append(
            {
                "source_index": i,
                "title": s.get("title"),
                "summary": s.get("summary"),
                "score": pct_score,
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
    # Deduplicate by article_id (or title when article_id is missing). If the
    # retriever returns multiple chunks from the same article, we want only one
    # entry per article in the final context. Keep the hit with the highest score.
    seen: dict = {}
    ordered_hits: List[Dict[str, Any]] = []
    for h in hits:
        aid = h.get("article_id") or h.get("title") or None
        # Use a composite key for None to preserve uniqueness per-hit
        key = aid if aid is not None else id(h)
        if key not in seen:
            seen[key] = h
            ordered_hits.append(h)
        else:
            # replace with higher-scoring hit if available
            try:
                prev_score = float(seen[key].get("score") or 0.0)
                cur_score = float(h.get("score") or 0.0)
            except Exception:
                prev_score = seen[key].get("score") or 0.0
                cur_score = h.get("score") or 0.0
            if cur_score > prev_score:
                seen[key] = h
                # also update ordered_hits
                for idx, oh in enumerate(ordered_hits):
                    if (oh.get("article_id") or oh.get("title") or None) == (h.get("article_id") or h.get("title") or None):
                        ordered_hits[idx] = h
                        break

    # Now sort the unique articles by descending score and pick top max_articles
    ordered_hits.sort(key=lambda x: float(x.get("score") or 0.0), reverse=True)
    top_sources = ordered_hits[:max_articles]

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
    mistral_key = os.environ.get("MISTRAL_API_KEY")

    if api_key:
        provider = "openai"
    elif mistral_key:
        provider = "mistral"
        api_key = mistral_key
    else:
        provider = "openai"

    print(f"Using provider={provider}")

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
            provider=provider,
        )

        print("\nANSWER:\n", out["answer"])
        print("\nSOURCES:")
        for s in out["sources"]:
            print(
                f"{s['source_index']}. {s.get('title')!r} (relevance=({s.get('score')})*100+%"
                )

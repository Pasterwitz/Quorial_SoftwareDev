from __future__ import annotations
import os
from typing import Any, Dict, List

import gradio as gr

from src.retriever import retrieve
from src.rag_pipeline import complete_rag_pipeline


def chat_fn(message: str, history: List[tuple[str, str]]) -> str:
    """
    Simple chat handler: runs the RAG pipeline once per user message.
    Uses OpenAI API key from OPENAI_API_KEY env var.
    """
    try:
        result: Dict[str, Any] = complete_rag_pipeline(
            query=message,
            api_key=None,
            top_k=10,
            context_window=2,
            max_articles=2,
            where=None,
        )
        answer = result.get("answer", "No answer returned.")
        sources = result.get("sources", [])

        if sources:
            src_lines = []
            for s in sources:
                title = s.get("title") or "Unknown title"
                article_id = s.get("article_id")
                src_lines.append(f"- [Source {s['source_index']}] {title} (id={article_id})")
            answer += "\n\nSources:\n" + "\n".join(src_lines)

        return answer

    except Exception as e:
        return f"Error while generating answer: {e}"



VALID_USER = "admin"
VALID_PASSWORD = "12345678"


def login_action(username: str, password: str):

    if username == VALID_USER and password == VALID_PASSWORD:
        msg = "Logged in successfully."
        return gr.update(visible=False), gr.update(visible=True), msg
    else:
        msg = "Wrong username or password."
        return gr.update(visible=True), gr.update(visible=False), msg




def build_app():
    with gr.Blocks(title="Quorial Demo") as demo:
        status = gr.Markdown("")

        with gr.Column(visible=True) as login_col:
            gr.Markdown("## Login")
            username = gr.Textbox(label="Username", placeholder="admin")
            password = gr.Textbox(label="Password", type="password", placeholder="********")
            login_btn = gr.Button("Log in")

        with gr.Column(visible=False) as chat_col:
            gr.Markdown("## Voxeurop News Assistant")
            gr.Markdown(
                "Ask questions about Voxeurop news articles. "
                "The assistant uses a RAG pipeline over your ChromaDB."
            )

            chat = gr.ChatInterface(
                fn=chat_fn,
                title="Voxeurop RAG Chat",
                textbox=gr.Textbox(placeholder="Ask about EU politics, migration, ..."),
            )

        login_btn.click(
            login_action,
            inputs=[username, password],
            outputs=[login_col, chat_col, status],
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    # By default launches on http://127.0.0.1:7860
    app.launch()
# Poetry Command Guide

## Overview
This document merges the original setup cheatsheet and the detailed backup notes into a single place. Follow the numbered setup once per machine, then rely on the everyday and maintenance sections to keep the RAG stack healthy.

## Requirements
- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Personal `MISTRAL_API_KEY` (needed for every LLM call)

## First-Time Setup (every new machine)
```bash
# 1) Clone and enter the repo
git clone https://github.com/Pasterwitz/Quorial_SoftwareDev-1.git
cd Quorial_SoftwareDev-1

# 2) Prepare environment variables
cp .env.example .env
# Add your MISTRAL_API_KEY and optional CHROMA/MODEL overrides to .env

# 3) Install Python dependencies
poetry install

# 4) Build the local Chroma vector store (skip clean/preprocess/chunk if data/ already exists!!!)
poetry run clean-data
poetry run preprocess-data
poetry run chunk-articles
poetry run rebuild-chroma   # REQUIRED to create the voxeurop_db directory, necessary to get the answers!

# 5) Create or refresh the Chroma vector store (voxeurop_db)
poetry run rebuild-chroma

# 6) Initialize the SQLite database once (creates instance/flaskauu.sqlite)
poetry run flask --app flask_quorial init-db

# 8) Export the API key for your shell session if you do not rely on .env
export MISTRAL_API_KEY=\"your_actual_key_here\"

# 9) Launch the Flask chat UI
poetry run chat-app
```
**Why each step matters:** The repository cannot ship API keys, the Chroma index, or the SQLite chat tables. Skipping any step above leaves the retriever empty or prevents the UI from persisting chats.

## Everyday Commands
- `poetry run chat-app` – Primary Flask UI (http://127.0.0.1:5000)  
- `poetry run test-retriever` – CLI dump of raw retrieval hits for a sample prompt  
- `poetry run rag-pipeline` – Executes the full retrieval + generation pipeline in CLI  
- `poetry run rebuild-chroma` – Fast rebuild when only embeddings need refreshing

## Testing
- `poetry run pytest` – Run the entire automated test suite.
- `poetry run pytest -s` – Run all tests and stream `print()` output to the terminal (useful for debugging).
- `poetry run pytest -k test_get_404` – Run only the tests whose names match the pattern after `-k` (here just `test_get_404`).

## Data & Index Maintenance
- Rebuild embeddings after touching processed articles:  
  ```bash
  rm -rf voxeurop_db
  poetry run chunk-articles      # only if chunked data changed
  poetry run rebuild-chroma
  ```
- Reset the SQLite DB (deletes chat history):  
  ```bash
  rm -f instance/flaskauu.sqlite
  poetry run flask --app flask_quorial init-db
  ```
- Refresh all preprocessing steps if the raw Voxeurop CSV changes:  
  ```bash
  poetry run clean-data
  poetry run preprocess-data
  poetry run chunk-articles
  poetry run rebuild-chroma
  ```

## Script Reference (`pyproject.toml`)
| Script | Command | Purpose |
| ------ | ------- | ------- |
| `chat-app` | `poetry run chat-app` | Flask RAG experience |
| `gradio-app` | `poetry run gradio-app` | Minimal Gradio UI |
| `clean-data` | `poetry run clean-data` | Clean raw Voxeurop CSV |
| `preprocess-data` | `poetry run preprocess-data` | Strip HTML, persist JSON |
| `chunk-articles` | `poetry run chunk-articles` | Split articles into chunks |
| `rebuild-chroma` | `poetry run rebuild-chroma` | Generate embeddings / persist Chroma |
| `rag-pipeline` | `poetry run rag-pipeline` | End-to-end CLI RAG test |
| `test-retriever` | `poetry run test-retriever` | Retrieval-only sanity check |

## Troubleshooting
- **“Script not found”** → Run `poetry install` to ensure virtualenv scripts exist.
- **Import errors** → Run commands from the repo root and prefix with `poetry run`.
- **Empty retrieval / Chroma errors** → Delete `voxeurop_db` and re-run `poetry run rebuild-chroma`.
- **Chats missing** → Run `poetry run flask --app flask_quorial init-db` once; avoid deleting `instance/flaskauu.sqlite` unless you intend to wipe history.
- **API key missing** → Confirm `MISTRAL_API_KEY` is set in `.env` or exported in your current shell with `export MISTRAL_API_KEY="your real API Key here"`

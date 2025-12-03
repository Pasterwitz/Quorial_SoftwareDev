# Poetry Command Guide

## 1. Prerequisites
- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Personal `MISTRAL_API_KEY` (required for the LLM call)

## 2. First-Time Setup (run every step on each new machine)
```bash
# Clone and enter the repo
git clone https://.../Quorial_SoftwareDev-1.git
cd Quorial_SoftwareDev-1

# Prepare environment variables
cp .env.example .env
# Edit .env and add your MISTRAL_API_KEY (and optional CHROMA/MODEL overrides)

# Install Python dependencies
poetry install

# Build the local Chroma vector store (skip clean/preprocess/chunk if data/ already exists!!!)
poetry run clean-data
poetry run preprocess-data
poetry run chunk-articles
poetry run rebuild-chroma   # REQUIRED to create the voxeurop_db directory, necessary to get the answers!

# Create the SQLite tables once
poetry run flask --app flask_quorial init-db

# Launch the Flask chat app
poetry run chat-app
```
**Why every step matters:** The repo does not contain your API keys, the Chroma index, or the SQLite database. If you skip any step above, the retriever will have no articles or the chat tables will not exist, and the UI will only return errors.

## 3. Everyday Commands
- `poetry run chat-app` – Run the Flask UI (http://127.0.0.1:5000)  
- #`poetry run gradio-app` – Minimal Gradio interface for quick RAG checks  
- `poetry run test-retriever` – Print raw retrieval hits for a sample query  
- `poetry run rag-pipeline` – Run the entire RAG flow from CLI

## 4. Data / Index Maintenance
- Rebuild after changing processed articles:  
  ```bash
  rm -rf voxeurop_db
  poetry run chunk-articles      # only if chunked data changed
  poetry run rebuild-chroma
  ```
- Reset the SQLite DB (warning: deletes chat history):  
  ```bash
  rm -f instance/flaskauu.sqlite
  poetry run flask --app flask_quorial init-db
  ```

## 5. Script Reference (defined in `pyproject.toml`)
| Script | Command | Purpose |
| ------ | ------- | ------- |
| `chat-app` | `poetry run chat-app` | Flask RAG application |
| `gradio-app` | `poetry run gradio-app` | Gradio demo UI |
| `clean-data` | `poetry run clean-data` | Clean raw Voxeurop CSV |
| `preprocess-data` | `poetry run preprocess-data` | Strip HTML, save JSON |
| `chunk-articles` | `poetry run chunk-articles` | Split articles into chunks |
| `rebuild-chroma` | `poetry run rebuild-chroma` | Create/persist embeddings |
| `rag-pipeline` | `poetry run rag-pipeline` | End-to-end RAG test |
| `test-retriever` | `poetry run test-retriever` | Retrieval-only sanity check |

## 6. Troubleshooting
- **“Script not found”** → Run `poetry install`
- **Import errors** → Ensure you’re in the repo root and use `poetry run ...`
- **Chroma errors / missing results** → Rebuild: `rm -rf voxeurop_db && poetry run rebuild-chroma`
- **Chats disappearing** → Run `poetry run flask --app flask_quorial init-db` only once; do not delete `instance/flaskauu.sqlite` unless you intend to wipe history.

# Poetry Command Guide

## 1. Prerequisites
- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Personal `MISTRAL_API_KEY` (required for the LLM call)

## 2. First-Time Setup (run every step on each new machine)
```bash
# Clone and enter the repo
git clone https://github.com/Pasterwitz/Quorial_SoftwareDev.git
cd Quorial_SoftwareDev

# Install Python dependencies
poetry install

# IMPORTANT: Check if data/ folder exists in the repo
ls -la data/chunked/chunked_articles.json

# Restore ChromaDB from existing chunked data
poetry run rebuild-chroma

# Verify database has data
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='./voxeurop_db')
collection = client.get_collection(name='voxeurop_articles')
print(f'Documents in database: {collection.count()}')
"
# Set API key for single session
export MISTRAL_API_KEY="your_actual_key_here"

# Launch the Flask chat app
poetry run chat-app

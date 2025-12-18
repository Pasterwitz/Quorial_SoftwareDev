# Quorial Chatbot

## Technical Documentation

### Project Overview

**Quorial** is a specialized chatbot application developed as part of the Software Engineering for Language Technologies course. 
The system is intended to provide civil society perspectives on political issues through a conversational interface.

**Repository Link:** https://github.com/Pasterwitz/Quorial_SoftwareDev  

---
## Quick Start Guide

### For End Users

Want to try Quorial? You have two available options:

**Option 1: Access the Live Deployment**

Visit our deployed application at:
**https://quorial.remotehost.top/auth/login**

No installation required! Simply:
1. Navigate to the URL above
2. Log in or create an account
3. Start asking questions about political and social issues
4. Click Send
5. Receive responses with civil society perspectives


**Option 2: Run Locally**
Want to run Quorial on your own machine? Follow these steps:

*First-Time Setup (every new machine)**

```bash
# 1) Clone and enter the repo
git clone https://github.com/Pasterwitz/Quorial_SoftwareDev.git
cd Quorial_SoftwareDev

# 2) Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# 3) Prepare environment variables
cp .env.example .env
# Add your MISTRAL_API_KEY and optional CHROMA/MODEL overrides to .env

# 4) Install Python dependencies
poetry install

# 5) Build the local Chroma vector store
# (skip clean/preprocess/chunk if data/ already exists!)
poetry run clean-data
poetry run preprocess-data
poetry run chunk-articles
poetry run rebuild-chroma   # REQUIRED to create voxeurop_db directory

# 6) Initialize the SQLite database once (creates instance/flaskauu.sqlite)
poetry run flask --app flask_quorial init-db

# 7) Export the API key for your shell session if you do not rely on .env
export MISTRAL_API_KEY="your_actual_key_here"

# 8) Launch the Flask chat UI
poetry run chat-app
```

**Everyday Commands (after initial setup)**
```bash
# Launch the application
poetry run chat-app

```
Access at `http://127.0.0.1:5000`

---

## Features

Quorial provides the following key features to help users understand political issues from civil society perspectives:

#### 1. Evidence-based answers
- Retrieves information from internal RepCo database

#### 2. Structured responses
- Summary, key insights, gaps in context, and sources with relevance scores

#### 3. User authentication
- Personal workspace with login

#### 4. Chat history
-  Save and revisit conversations

#### 5. PDF export
- Export full conversations with insights and sources

--- 

## Technology stack

1. **Backend**: Flask (Python)
2. **Database**: SQLite (chat history), Chroma (vector database)
3. **LLM**: Mistral AI API
4. **Frontend**: HTML, CSS
---

## Dataset

**Source**: Voxeurope articles
**Languages**: English (595), German (445), Russian (301)
**Format**: CSV -> JSON Lines -> Vector embeddings
**Columns**: content, contentItemUid, contentUrl, languageCode, summary, title, uid

---

## Architecture

```
User Query → Flask App → Chroma Vector Search → Mistral AI → Response
                ↓
           SQLite DB (chat history)
```

**Data Flow:**
1. User submits query
2. Semantic search in Chroma database
3. Retrieved articles sent to Mistral AI as context
4. AI generates response with sources
5. Chat saved to SQLite

---

## Project Structure

```
Quorial_SoftwareDev/
├── data/                    # chunked, cleaned, preprocessed datasets
├── flask_quorial/          # Main Flask application
│   ├── static/pics/        
│   ├── templates/         
│   ├── tools/            
│   ├── __init__.py         
│   ├── auth.py         
│   ├── chat.py             # Chat functionality
│   ├── db.py               # Database operations
│   └── state.py            
├── src/                    # Source modules
├── tests/                  # Test suite
├── .env.example            # Environment template
├── .gitattributes          
├── .gitignore              
├── POETRY_COMMANDS.md      # Poetry reference
├── README.md               # This file
├── poetry.lock             # Locked dependencies
├── poetry.toml             # Poetry config
├── pyproject.toml          # Project dependencies
└── run_chat_app.py         # Application entry point
```

---

## Configuration

Required in `.env`:
```bash
MISTRAL_API_KEY=your-key-here
```

Get Mistral API key from: https://mistral.ai
For detailed configuration options and troubleshooting, see `POETRY_COMMANDS.md`

---

## Testing

```bash
poetry run pytest                           # Run all test
poetry run pytest -s                        # Run with output
poetry run pytest -k test_name              # Run specific test
```
For complete testing guide and maintenance commands, see `POETRY_COMMANDS.md`

---

## Contributors

- [Zhiyi Chen](https://github.com/Jojelu)
- [Angelina Radovanov](https://github.com/angelinaradovanov)
- [Zarina Beisenbayeva](https://github.com/zariness00)
- [Polina Bogdanova](https://github.com/01ponyo)

**Product Owner**: [Alexander Baratsits]  
**Development Team**: [Zhiyi Chen, Angelina Radovanov, Zarina Beisenbayeva, Polina Bogdanova]

---

## License

Academic project for Software Engineering for Language Technologies course.

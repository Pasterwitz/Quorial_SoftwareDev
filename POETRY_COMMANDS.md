# 🎯 Poetry Commands for QUORIAL Project

## Available Poetry Scripts

After adding Poetry scripts to `pyproject.toml`, you can now run all project components using simple `poetry run` commands:

### 🚀 **Main Applications**

#### **Flask Chat Application**
```bash
poetry run chat-app
```
- Runs the main QUORIAL Flask web application
- Starts server at http://127.0.0.1:5000
- Includes beautiful slideshow login and RAG-powered chat

#### **Gradio Interface**
```bash
poetry run gradio-app
```
- Launches the Gradio web interface
- Starts server at http://127.0.0.1:7860
- Simple chat interface for testing RAG functionality

---

### 📊 **Data Processing Scripts**

#### **Clean Raw Data**
```bash
poetry run clean-data
```
- Cleans and preprocesses raw article data
- Removes duplicates and formats content

#### **Preprocess Data**
```bash
poetry run preprocess-data
```
- Advanced preprocessing of article content
- Prepares data for chunking and embedding

#### **Chunk Articles**
```bash
poetry run chunk-articles
```
- Splits articles into manageable chunks
- Optimizes chunk size for better RAG retrieval

---

### 🗄️ **ChromaDB Management**

#### **Upload Chunks (Individual)**
```bash
poetry run upload-chunks
```
- Uploads chunked articles to ChromaDB one by one
- Good for testing and small datasets

#### **Batch Upload (Recommended)**
```bash
poetry run batch-upload
```
- Efficiently uploads chunks in batches to ChromaDB
- Faster processing for large datasets
- Includes progress tracking

#### **Rebuild ChromaDB**
```bash
poetry run rebuild-chroma
```
- Completely rebuilds the ChromaDB vector database
- Useful when changing embedding models or collection settings

---

### 🤖 **RAG Pipeline Operations**

#### **RAG Pipeline**
```bash
poetry run rag-pipeline
```
- Runs the complete RAG pipeline end-to-end
- Tests query processing and response generation

#### **Test Retriever**
```bash
poetry run test-retriever
```
- Tests the retrieval functionality
- Validates semantic search capabilities

---

## 📋 **Common Usage Patterns**

### **Fresh Setup Process**
```bash
# 1. Install dependencies
poetry install

# 2. Process and upload data (if needed)
poetry run clean-data
poetry run preprocess-data
poetry run chunk-articles
poetry run batch-upload

# 3. Start the application
poetry run chat-app
```

### **Development Workflow**
```bash
# Test RAG functionality
poetry run test-retriever

# Run Gradio for quick testing
poetry run gradio-app

# Launch main Flask application
poetry run chat-app
```

### **Data Management**
```bash
# Rebuild database with new data
poetry run rebuild-chroma
poetry run batch-upload

# Test the updated system
poetry run rag-pipeline
```

---

## 🛠️ **Poetry Configuration Details**

The scripts are defined in `pyproject.toml` under `[tool.poetry.scripts]`:

```toml
[tool.poetry.scripts]
# Main Applications
chat-app = "run_chat_app:main"
gradio-app = "src.app_gradio:main"

# Data Processing Scripts
clean-data = "src.clean_raw_data:main"
preprocess-data = "src.preprocess:main"
chunk-articles = "src.chunking_articles:main"

# ChromaDB Management
upload-chunks = "src.upload_chunk:main"
batch-upload = "src.batch_upload:main"
rebuild-chroma = "src.rebuild_chroma:main"

# RAG Pipeline
rag-pipeline = "src.rag_pipeline:main"
test-retriever = "src.retriever:main"
```

Each script points to a `main()` function in the respective module, ensuring consistent entry points across the project.

---

## 🎯 **Benefits of Poetry Scripts**

1. **Simplified Commands**: No need to remember complex Python module paths
2. **Environment Management**: Poetry handles virtual environment activation
3. **Dependency Resolution**: Ensures all dependencies are available
4. **Cross-Platform**: Works consistently across Windows, macOS, and Linux
5. **Professional Workflow**: Industry-standard approach to Python project management

---

## 🔧 **Troubleshooting**

### **Script Not Found**
If you get "script not found" errors:
```bash
poetry install  # Reinstall dependencies and scripts
```

### **Import Errors**
If you encounter import errors:
```bash
# Make sure you're in the project root directory
cd /path/to/Quorial_SoftwareDev-1
poetry run chat-app
```

### **Database Issues**
If ChromaDB has issues:
```bash
poetry run rebuild-chroma  # Rebuild the database
poetry run batch-upload    # Re-upload data
```

---

## 📚 **Example Usage**

### **Start the Main Application**
```bash
$ poetry run chat-app
Database initialized successfully!
Starting Chat Application...
Access the application at: http://127.0.0.1:5000
Press Ctrl+C to stop the server
 * Serving Flask app 'flask_quorial'
 * Debug mode: on
```

### **Test RAG Functionality**
```bash
$ poetry run test-retriever
Testing ChromaDB retrieval...
Query: "EU migration policy"
Found 5 relevant articles
Top result: "European Migration Crisis: Policy Responses"
```

This Poetry setup provides a professional, maintainable way to manage and run all components of the QUORIAL project!

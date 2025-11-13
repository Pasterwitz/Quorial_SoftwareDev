import chromadb
import json
from tqdm import tqdm

def load_chunked_articles(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def upload_in_batches(chunked_articles, batch_size=100):
    client_chroma = chromadb.PersistentClient(path="../voxeurop_db")
    collection = client_chroma.get_or_create_collection(
        name="voxeurop_articles", 
        metadata={"hnsw:space": "cosine"}
    )
    
    print(f"ChromaDB collection: {client_chroma.list_collections()}")
    print(f"Starting upload of {len(chunked_articles)} chunks in batches of {batch_size}")
    
    # Clear existing data first
    try:
        client_chroma.delete_collection("voxeurop_articles")
        collection = client_chroma.create_collection(
            name="voxeurop_articles", 
            metadata={"hnsw:space": "cosine"}
        )
        print("Cleared existing collection")
    except:
        pass
    
    for i in tqdm(range(0, len(chunked_articles), batch_size), desc="Uploading batches"):
        batch = chunked_articles[i:i + batch_size]
        
        documents = []
        metadatas = []
        ids = []
        
        for idx, chunk in enumerate(batch):
            doc_text = chunk['document']
            metadata = chunk['metadata']
            
            # Clean metadata
            clean_metadata = {}
            for key, value in metadata.items():
                if value is not None and value != "":
                    clean_metadata[key] = value
            
            if 'article_id' not in clean_metadata:
                clean_metadata['article_id'] = i + idx
            if 'chunk_idx' not in clean_metadata:
                clean_metadata['chunk_idx'] = 0
            
            documents.append(doc_text)
            metadatas.append(clean_metadata)
            ids.append(f"chunk_{i + idx}")
        
        # Batch upload
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        if (i + batch_size) % 500 == 0:  # Progress check every 500 docs
            current_count = collection.count()
            print(f"Progress: {current_count} documents uploaded")
    
    final_count = collection.count()
    print(f"\nUpload complete! Total documents: {final_count}")
    
    # Test search
    print("\nTesting search functionality...")
    test_queries = [
        "EU migration policy",
        "Bulgaria politics",
        "European Union"
    ]
    
    for query in test_queries:
        results = collection.query(query_texts=[query], n_results=2)
        print(f"\nQuery: '{query}' - Found {len(results['documents'][0])} results")
        if results['documents'][0]:
            first_result = results['metadatas'][0][0]
            print(f"  Top result: {first_result.get('title', 'No title')}")

def main():
    """Main function to run batch upload of chunked articles to ChromaDB"""
    import os
    
    # Adjust paths to work from project root
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'chunked', 'chunked_articles.json')
    
    print("Loading chunked articles...")
    chunked_articles = load_chunked_articles(data_path)
    upload_in_batches(chunked_articles, batch_size=50)

if __name__ == "__main__":
    main()

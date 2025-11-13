import chromadb
import json

def load_chunked_articles(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        chunked_articles = json.load(file)

    return chunked_articles



client_chroma = chromadb.PersistentClient(path="./voxeurop_db")
collection = client_chroma.get_or_create_collection(name = "voxeurop_articles", metadata = {"hnsw:space": "cosine"})
#verifying my collection
print(f"ChromaDB collection {client_chroma.list_collections()}")

chunked_articles = load_chunked_articles('../data/chunked/chunked_articles.json')

print("Adding chunks to ChromaDB...")
for idx, chunk in enumerate(chunked_articles):
    doc_text = chunk['document']  
    metadata = chunk['metadata']

    #some articles miss the summary field; chromadb cannot store None values, so we clean the metadata
    clean_metadata = {}
    for key, value in metadata.items():
        if value is not None and value != "":
            clean_metadata[key] = value
    
    if 'article_id' not in clean_metadata:
        clean_metadata['article_id'] = idx
    if 'chunk_idx' not in clean_metadata:
        clean_metadata['chunk_idx'] = 0

    collection.add(
        documents=[doc_text],
        metadatas=[clean_metadata], 
        ids=[f"chunk_{idx}"]
    )

print("Testing")
test_query = "Bulgaria EU politics"
search_results = collection.query(query_texts=[test_query], n_results=3)

for idx, result in enumerate(search_results["documents"][0]):
    metadata = search_results["metadatas"][0][idx]
    print(f"\n--- Result {idx + 1} ---")
    print(f"Title: {metadata['title']}")
    print(f"Summary: {metadata.get('summary', 'N/A')[:100]}...")
    print(f"Chunk: {result[:200]}...")

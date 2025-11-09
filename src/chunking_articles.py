import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
def load_preprocessed_articles(file_path):
    articles = []
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            articles = json.load(file)
        except json.JSONDecodeError:
            file.seek(0) 
            for line in file:
                line = line.strip()
                if line:
                    articles.append(json.loads(line))
    return articles

def chunk_articles(articles):
    text_splitter = RecursiveCharacterTextSplitter(
    separators=[". ", "? ", "! "],
    chunk_size=2000,
    chunk_overlap=300,)

    chunked_articles = []

    for idx, article in enumerate(articles):
        title = article.get("title", "")
        summary = article.get("summary", "")
        content = article.get("content", "")

        docs = text_splitter.create_documents(
            texts=[content],
            metadatas=[{
                'article_id': idx,
                'title': title,
                'summary': summary,
            }]
        )
    
        for chunk_idx, doc in enumerate(docs):
            doc.metadata['chunk_idx'] = chunk_idx
            #doc.metadata['total_chunks'] = len(docs)
            chunked_articles.append(doc)
    

    return chunked_articles
def save_chunked_articles(chunked_articles, output_file_path):

    import os

def save_chunked_articles(chunked_articles, output_file_path):
 
    #convert Document objects to dictionaries
    chunks_as_dicts = []
    for doc in chunked_articles:
        chunks_as_dicts.append({
            'document': doc.page_content,
            'metadata': doc.metadata
        })
    
    # NOW save the dictionaries
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(chunks_as_dicts, file, ensure_ascii=False, indent=4)
    print("Chunked articles saved to", output_file_path)

    articles_total = len(set([chunk['metadata']['article_id'] for chunk in chunks_as_dicts]))
    average_chunks_article = len(chunks_as_dicts) / articles_total 
    print(f"Total articles processed: {articles_total}")
    print("Total chunks created:", len(chunks_as_dicts))


def main():
    input_file_path = 'data/preprocessed/voxeurop_cleaned_content_v2.json'
    output_file_path = 'data/chunked/chunked_articles.json'

    articles = load_preprocessed_articles(input_file_path)
    chunked_articles = chunk_articles(articles)
    save_chunked_articles(chunked_articles, output_file_path)

    if chunked_articles:
        print("Sample chunked article:")
        sample = chunked_articles[0]
        print(f"Document: {sample.page_content}...")
        print(f"Metadata: {sample.metadata}")

if __name__ == "__main__":
    main()


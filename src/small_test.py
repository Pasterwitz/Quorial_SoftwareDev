if __name__ == "__main__":
    from src.retriever import retrieve, print_retrieval_results

    q = "What does Voxeurop report about Bulgaria and EU politics?"
    hits = retrieve(q, top_k=5, context_size=2, where=None)
    print_retrieval_results(hits, max_content_length=300)
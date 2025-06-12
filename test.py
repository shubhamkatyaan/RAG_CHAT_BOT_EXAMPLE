# test_rag.py
from app.rag.retriever import retrieve
from app.rag.llm       import generate

def main():
    query = "What is the loaction of comapny"
    ctx   = retrieve(query)
    answer = generate(query, ctx)
    print("Answer:\n", answer)
    print("\nTop contexts:")
    for c in ctx:
        print(f"- ({c['source']} chunk {c['chunk_id']}): {c['text'][:200]}…")

if __name__ == "__main__":
    main()

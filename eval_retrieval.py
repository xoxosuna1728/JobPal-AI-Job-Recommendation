"""Retrieval eval: does the right job appear in the top 3 results? No API key needed.

Run: python eval_retrieval.py
"""
from search import JobIndex

# (query, titles that count as a correct answer)
CASES = [
    ("I want to build chatbots and agents with LLMs", ["LLM Engineer Intern"]),
    ("semantic search with embeddings internship", ["Search Engineer Intern"]),
    ("python flask backend internship", ["Backend Developer Intern"]),
    ("object detection YOLO computer vision", ["Computer Vision", "Machine Learning Intern (Computer Vision)"]),
    ("recommendation and ranking systems", ["Recommendation Systems Intern"]),
    ("RAG pipeline over documents", ["AI Backend Intern (RAG)", "NLP Engineer"]),
    ("android app development", ["Android Developer Intern"]),
    ("prompt engineering and evaluating LLM answers", ["Prompt Engineer", "LLM Engineer Intern"]),
    ("SQL dashboards and data cleaning", ["Data Analyst Intern"]),
    ("docker aws ci/cd", ["DevOps Intern"]),
]


def main():
    index = JobIndex()
    hits = 0
    for q, expected in CASES:
        top = [r["title"] for r in index.search(q, top_k=3)]
        ok = any(any(e in t for e in expected) for t in top)
        hits += ok
        print(f"{'PASS' if ok else 'FAIL'}  {q!r}\n      top 3: {top}")
    print(f"\nBackend: {index.backend}")
    print(f"Recall@3: {hits}/{len(CASES)} = {hits / len(CASES):.0%}")


if __name__ == "__main__":
    main()

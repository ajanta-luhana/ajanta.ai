"""Validate and report on the knowledge base: python -m scripts.ingest"""
from app.core.config import get_settings
from app.rag.retriever import Retriever

r = Retriever(get_settings().knowledge_dir)
print(f"Indexed {len(r.chunks)} chunks from {r.doc_count()} documents with content.")
for src in sorted({c.source for c in r.chunks}):
    print(f"  {src}: {sum(1 for c in r.chunks if c.source == src)} chunks")

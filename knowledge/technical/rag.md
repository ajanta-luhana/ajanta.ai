# Retrieval-Augmented Generation (RAG)

## What it is
RAG grounds an LLM's answer in documents retrieved at query time instead of relying on the model's memory. The pipeline is: ingest and chunk documents, embed the chunks, store them in a vector index, retrieve the top-k chunks for a query, and prompt the LLM with those chunks as context.

## Why it reduces hallucination
Answers can cite the retrieved evidence, and the system can refuse to answer when retrieval finds nothing relevant. Quality depends on chunking, retrieval relevance, and prompt constraints.

## Common improvements
Hybrid search (keyword plus vector), reranking, query rewriting, metadata filtering, and a post-generation grounding check.

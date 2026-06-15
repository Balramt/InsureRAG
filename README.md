insurerag/
│
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── official/
│   │   │   ├── vvg/
│   │   │   └── vvg_infov/
│   │   │
│   │   └── internal/
│   │       ├── internal_customer_information_policy.md
│   │       └── internal_product_approval_checklist.md
│   │
│   ├── processed/
│   │   ├── chunks/
│   │   └── metadata/
│   │
│   └── evaluation/
│       ├── test_questions.json
│       └── expected_sources.json
│
├── notebooks/
│   └── 00_exploration.ipynb
│
├── src/
│   └── insurerag/
│       ├── __init__.py
│       ├── config.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── document.py
│       │   ├── chunk.py
│       │   └── answer.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── loaders.py
│       │   ├── cleaners.py
│       │   ├── chunkers.py
│       │   └── metadata.py
│       │
│       ├── embeddings/
│       │   ├── __init__.py
│       │   └── local_embeddings.py
│       │
│       ├── vectorstore/
│       │   ├── __init__.py
│       │   └── qdrant_store.py
│       │
│       ├── retrieval/
│       │   ├── __init__.py
│       │   └── retriever.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── ollama_client.py
│       │   └── hf_client.py
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── prompts.py
│       │   ├── chain.py
│       │   └── citation_formatter.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   └── rag_service.py
│       │
│       ├── evaluation/
│       │   ├── __init__.py
│       │   └── test_questions.py
│       │
│       ├── app/
│       │   ├── __init__.py
│       │   ├── cli.py
│       │   └── streamlit_app.py
│       │
│       └── api/
│           ├── __init__.py
│           ├── main.py
│           └── routes.py
│
├── scripts/
│   ├── ingest.py
│   └── query.py
│
└── tests/
    ├── test_chunking.py
    ├── test_metadata.py
    └── test_retrieval.py
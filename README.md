# Private document Q&A tool — accurate answers with citations, no hallucination

![status](https://img.shields.io/badge/status-demo-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![fastapi](https://img.shields.io/badge/backend-FastAPI-009688)

![demo screenshot placeholder](screenshots/demo.png)
*(Screenshot: capture the upload state + an answered question with a visible source citation.)*

**Live demo:** _add your deployed link here once hosted_

## The business problem

Staff waste hours digging through policy PDFs, contracts, and manuals to answer simple questions. Generic chatbots make this worse by confidently inventing answers that aren't actually in the document. This tool only answers from the real text you give it — and tells you plainly when something isn't covered, instead of guessing.

## Architecture

```
rag-document-qa/
├── backend/
│   ├── config/
│   │   └── prompts.py        # System prompt + chunking/retrieval parameters
│   ├── core/
│   │   ├── ingestion.py      # PDF extraction + chunking
│   │   └── retrieval.py      # Vector-style retrieval + answer generation
│   ├── main.py                # FastAPI route definitions only
│   ├── .env.example           # Copy to .env — never commit real keys
│   └── requirements.txt
├── frontend/
│   └── index.html             # Drag-and-drop upload + Q&A UI, no build step
└── README.md
```

**Stack:** `Python` · `FastAPI` · `scikit-learn (TF-IDF retrieval)` · `pdfplumber` · `OpenAI API` · `HTML/CSS/JS`

## Key features

- Upload any PDF and it's automatically chunked and indexed for search
- Every answer includes the exact source file and page number it came from
- Explicitly says "not covered" instead of fabricating an answer when the document doesn't have it
- Runs fully offline via TF-IDF retrieval with zero API key, or with an OpenAI key for more natural generated answers
- Retrieval and ingestion logic fully isolated in `core/`, independent of the API route layer

## Security

- API keys loaded from environment variables via `.env` (gitignored) — never hardcoded
- CORS restricted to the real frontend domain before any client deployment, not left at `*`
- Document contexts are isolated per session in this demo store; a production multi-client version should scope retrieval per client/tenant so one client's documents are never retrievable by another

## How to run it locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # add your OPENAI_API_KEY, or leave blank for offline retrieval mode
uvicorn main:app --reload --port 8000
```

**Frontend:**
Open `frontend/index.html` in a browser. Upload a PDF, then ask questions — talks to the backend at `http://localhost:8000` by default.

## Deployment

- **Backend:** Render, Railway, or Fly.io for the FastAPI app. Set `OPENAI_API_KEY` via the host's environment variable panel.
- **Frontend:** Vercel, Netlify, or GitHub Pages — update `API_BASE` in `index.html` before publishing.

## What I'd improve next

- Swap the in-memory chunk store for a real vector database (Supabase/pgvector, ChromaDB, or FAISS with persistence)
- Use real embeddings (OpenAI or a local sentence-transformer model) instead of TF-IDF for better semantic matching on paraphrased questions
- Add multi-tenant isolation so multiple clients' documents can be safely hosted on one instance without cross-visibility

## Contact

[Your LinkedIn] · [Your portfolio link]

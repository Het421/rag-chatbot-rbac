# RAG Chatbot with RBAC

Internal company chatbot that answers employee questions 
using role-aware PDF document retrieval.

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **RAG:** LangChain, Groq (llama-3.1-8b-instant)
- **Vector DB:** Qdrant Cloud
- **Embeddings:** HuggingFace all-MiniLM-L6-v2
- **Database:** PostgreSQL
- **Search:** Hybrid (BM25 + Semantic)

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your values
5. Run backend: `uvicorn main:app --reload` (from `backend/`)
6. Run frontend: `streamlit run app.py` (from `frontend/`)

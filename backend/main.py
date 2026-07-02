from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router
from documents.router import router as documents_router
from rag.router import router as rag_router
from chat.router import router as chat_router

app = FastAPI(
    title="Company RAG Chatbot API",
    description="Internal RAG chatbot with role-based PDF access",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"status": "RAG Chatbot API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
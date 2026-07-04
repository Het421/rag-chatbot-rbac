from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from auth.router import router as auth_router
from documents.router import router as documents_router
from rag.router import router as rag_router
from chat.router import router as chat_router

app = FastAPI(
    title="ColleagueAI API",
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

# ─────────────────────────────────
# Serve frontend static files
# ─────────────────────────────────
frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'frontend')
)
app.mount(
    "/static",
    StaticFiles(directory=frontend_path),
    name="static"
)


# ─────────────────────────────────
# HTML page routes
# ─────────────────────────────────
@app.get("/")
def serve_login():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/chat")
def serve_chat():
    return FileResponse(os.path.join(frontend_path, "chat.html"))


@app.get("/admin")
def serve_admin():
    return FileResponse(os.path.join(frontend_path, "admin.html"))


@app.get("/profile")
def serve_profile():
    return FileResponse(os.path.join(frontend_path, "profile.html"))


# ─────────────────────────────────
# API routers
# ─────────────────────────────────
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
"""
main.py — Entry point da API Holtech (MVC + DDD)

Substitui o antigo api.py monolítico.
Execute com:  uvicorn main:app --host 0.0.0.0 --port 8000
"""

import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.infrastructure.database.init_db import init_db
from app.presentation.controllers.auth_controller import router as auth_router
from app.presentation.controllers.usuario_controller import router as usuario_router
from app.presentation.controllers.historico_controller import router as historico_router
from app.presentation.controllers.auditoria_controller import router as auditoria_router
from config import APP_NAME, APP_VERSION, CORS_ALLOWED_ORIGINS, LP_PATH, LOGIN_PATH, CRUD_PATH, AUDITORIA_PATH, SERVE_STATIC_FRONTEND

# ─────────────────────────────────────────────────
# Criação da aplicação FastAPI
# ─────────────────────────────────────────────────
app = FastAPI(
    title=APP_NAME,
    description="Sistema de Gestão de Usuários — arquitetura MVC com DDD",
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─────────────────────────────────────────────────
# Middleware CORS
# ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Saúde"])
def api_health():
    """Healthcheck usado por Kubernetes, release e monitoramento."""
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/health", tags=["Saúde"])
def health():
    """Alias simples para healthcheck fora do prefixo /api."""
    return api_health()

# ─────────────────────────────────────────────────
# Evento de startup: inicializa o banco de dados
# ─────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    init_db()

# ─────────────────────────────────────────────────
# Routers (controllers)
# ─────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(historico_router)
app.include_router(auditoria_router)

# ─────────────────────────────────────────────────
# Arquivos estáticos do frontend (opcional para execução full-stack/local)
# ─────────────────────────────────────────────────
if SERVE_STATIC_FRONTEND and os.path.isdir(LOGIN_PATH):
    app.mount("/login", StaticFiles(directory=LOGIN_PATH, html=True), name="login")

if SERVE_STATIC_FRONTEND and os.path.isdir(CRUD_PATH):
    app.mount("/crud", StaticFiles(directory=CRUD_PATH, html=True), name="crud")

if SERVE_STATIC_FRONTEND and os.path.isdir(AUDITORIA_PATH):
    app.mount("/app", StaticFiles(directory=AUDITORIA_PATH, html=True), name="app")

if SERVE_STATIC_FRONTEND and os.path.isdir(LP_PATH):
    app.mount("/", StaticFiles(directory=LP_PATH, html=True), name="lp")

# ─────────────────────────────────────────────────
# Execução direta
# ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

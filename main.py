#!/usr/bin/env python3
"""
Script principal - Sistema de Tickets Prefeitura
"""
import sys
import os
from pathlib import Path

# Verificar ambiente virtual apenas em desenvolvimento local (não no Docker/produção)
# No Docker/Railway, o ambiente já está isolado e não precisa de venv
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = os.getenv("PORT")  # Railway/Docker sempre define PORT
IS_DOCKER = (
    os.path.exists("/.dockerenv") or  # Docker padrão
    os.getenv("RAILWAY_ENVIRONMENT") is not None or  # Railway
    os.getenv("RAILWAY") is not None or  # Railway (alternativo)
    PORT is not None  # Se PORT está definido, provavelmente é deploy
)

# Apenas verificar venv em desenvolvimento local (não em Docker/Railway)
if not IS_DOCKER and ENVIRONMENT == "development":
    # Verificar se está no venv
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if not in_venv:
        # Não está no venv, tentar usar o venv do projeto
        PROJECT_DIR = Path(__file__).resolve().parent
        VENV_PYTHON = PROJECT_DIR / "venv" / "bin" / "python"
        
        if VENV_PYTHON.exists():
            # Reexecutar usando o Python do venv
            os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
        else:
            print("❌ Ambiente virtual não encontrado!")
            print("📦 Execute: python3 -m venv venv")
            print("📦 Depois: pip install -r requirements.txt")
            sys.exit(1)

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies.database import Base, engine
from app.routes import (
    auth_router,
    user_router,
    ticket_router, 
    tech_router,
    admin_router,
    avatar_router,
    attachment_router
)

# Carregar variáveis de ambiente
load_dotenv()

# === CRIAÇÃO AUTOMÁTICA DO BANCO E TABELAS ===
def init_db():
    """Cria todas as tabelas se não existirem"""
    Base.metadata.create_all(bind=engine)
    print("Banco de dados inicializado!")

# Inicializa o banco ao iniciar o app
init_db()

app = FastAPI(title="Sistema de Tickets - Prefeitura", version="1.0.0")

# Configuração de CORS - Seguro para produção
def get_allowed_origins():
    """Retorna lista de origens permitidas baseada em variáveis de ambiente"""
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    environment = os.getenv("ENVIRONMENT", "development")
    
    if env_origins:
        # Separar por vírgula e remover espaços
        origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    else:
        origins = []
    
    # Em desenvolvimento, adicionar localhost
    if environment != "production":
        development_origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        # Adicionar apenas se não estiverem já na lista
        for origin in development_origins:
            if origin not in origins:
                origins.append(origin)
    
    # Se não houver origens configuradas e estiver em produção, retornar lista vazia (mais seguro)
    # Em desenvolvimento, permitir todas as origens localhost
    if not origins and environment != "production":
        return ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas organizadas por módulos
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(ticket_router)
app.include_router(tech_router)
app.include_router(admin_router)
app.include_router(avatar_router)
app.include_router(attachment_router)

# Arquivos estáticos (avatars)
# Garante que a pasta 'static' exista e usa caminho absoluto para evitar erros
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')

# Health check endpoint
@app.get("/health")
def health_check():
    """Endpoint de health check para monitoramento"""
    environment = os.getenv("ENVIRONMENT", "development")
    return {
        "status": "ok",
        "environment": environment,
        "cors_origins": get_allowed_origins()
    }

# Rodar servidor diretamente
if __name__ == "__main__":
    import uvicorn
    environment = os.getenv("ENVIRONMENT", "development")
    host = "0.0.0.0" if environment == "production" else "127.0.0.1"
    port = int(os.getenv("PORT", "8000"))
    reload = environment != "production"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload)

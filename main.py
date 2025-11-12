#!/usr/bin/env python3
"""
Script principal - Sistema de Tickets Prefeitura
"""
import sys
import os
import asyncio
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

app = FastAPI(title="Sistema de Tickets - Prefeitura", version="1.0.0")

# === CRIAÇÃO AUTOMÁTICA DO BANCO E TABELAS ===
def init_db():
    """Cria todas as tabelas se não existirem"""
    import time
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Tentativa {attempt + 1}/{max_retries}: Criando tabelas do banco de dados...")
            Base.metadata.create_all(bind=engine)
            print("✅ Banco de dados inicializado!")
            return
        except Exception as e:
            print(f"⚠️ Tentativa {attempt + 1} falhou: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Aguardando {retry_delay} segundos antes de tentar novamente...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Erro ao inicializar banco de dados após {max_retries} tentativas: {e}")
                import traceback
                traceback.print_exc()
                print("⚠️ O servidor continuará, mas algumas funcionalidades podem não funcionar.")

# Inicializa o banco ao iniciar o app (usando startup event)
@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar o servidor"""
    print("🚀 Iniciando servidor...")
    print(f"📍 Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"🔌 Porta: {os.getenv('PORT', '8000')}")
    print("🌐 Servidor pronto para receber requisições!")
    # Inicializar banco em background para não travar startup
    import asyncio
    asyncio.create_task(init_db_async())

async def init_db_async():
    """Inicializa banco de dados de forma assíncrona"""
    await asyncio.sleep(1)  # Aguardar um pouco antes de inicializar
    print("⏳ Inicializando banco de dados em background...")
    init_db()

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
    
    # Se não houver origens configuradas e estiver em produção, permitir todas (temporário)
    # TODO: Configurar ALLOWED_ORIGINS após deploy do frontend
    if not origins:
        if environment == "production":
            return ["*"]  # Permitir todas temporariamente
        else:
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

# Root endpoint
@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "message": "Sistema de Tickets - Prefeitura API",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint (simplificado para responder rápido)
@app.get("/health")
def health_check():
    """Endpoint de health check para monitoramento"""
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Resposta rápida sem verificar banco (para não travar)
    return {
        "status": "ok",
        "environment": environment,
        "message": "Server is running"
    }

# Rodar servidor diretamente
if __name__ == "__main__":
    import uvicorn
    environment = os.getenv("ENVIRONMENT", "development")
    host = "0.0.0.0" if environment == "production" else "127.0.0.1"
    try:
        port = int(os.getenv("PORT", "8000"))
    except ValueError:
        port = 8000
        print(f"⚠️ AVISO: PORT tem valor inválido, usando padrão {port}")
    reload = environment != "production"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload)

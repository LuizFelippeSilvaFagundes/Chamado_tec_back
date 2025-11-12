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
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
import logging
import time
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema de Tickets - Prefeitura", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração de CORS (deve vir antes dos outros middlewares)
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
            # Em produção, permitir todas as origens se não configurado
            return ["*"]
        else:
            return ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    return origins

origins_list = get_allowed_origins()
# Se for "*", não usar allow_credentials (incompatível)
if "*" in origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Middleware de logging de requisições
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição
        logger.info(f"📥 {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"❌ {request.method} {request.url.path} - ERRO após {process_time:.3f}s: {e}")
            raise

app.add_middleware(LoggingMiddleware)

# Middleware de tratamento de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura todos os erros não tratados"""
    logger.error(f"❌ Erro não tratado: {exc}", exc_info=True)
    logger.error(f"📍 Path: {request.url.path}")
    logger.error(f"📍 Method: {request.method}")
    
    # Log do traceback completo
    logger.error(f"📍 Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "error": str(exc),
            "path": request.url.path
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Trata erros HTTP"""
    logger.warning(f"⚠️ HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Trata erros de validação"""
    logger.warning(f"⚠️ Validação falhou: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# Inicializa o banco ao iniciar o app (usando startup event)
@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar o servidor"""
    logger.info("🚀 Servidor FastAPI iniciado!")
    logger.info(f"📍 Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🔌 Porta: {os.getenv('PORT', '8000')}")
    
    # Tentar inicializar o banco de dados (criar tabelas se não existirem)
    try:
        logger.info("🔧 Inicializando banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.error(f"⚠️ Erro ao inicializar banco de dados: {e}")
        logger.error(f"📍 Traceback: {traceback.format_exc()}")
        # Não crashar o servidor se o banco falhar (pode ser problema temporário)
    
    logger.info("🌐 Servidor pronto para receber requisições!")

# Root endpoint (definir primeiro para garantir que sempre funcione)
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
    db_status = "unknown"
    
    # Tentar conectar ao banco de dados (rápido, sem timeout longo)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        logger.warning(f"⚠️ Banco de dados não acessível no health check: {e}")
        db_status = "disconnected"
    
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "environment": environment,
        "database": db_status,
        "message": "Server is running"
    }

# Endpoint de teste simples (sem banco de dados)
@app.get("/test")
def test_endpoint():
    """Endpoint de teste simples"""
    return {
        "status": "ok",
        "message": "Endpoint de teste funcionando",
        "timestamp": str(os.path.getmtime(__file__) if os.path.exists(__file__) else "unknown")
    }

# Incluir rotas organizadas por módulos
try:
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(ticket_router)
    app.include_router(tech_router)
    app.include_router(admin_router)
    app.include_router(avatar_router)
    app.include_router(attachment_router)
    print("✅ Rotas registradas com sucesso!")
except Exception as e:
    print(f"⚠️ Erro ao registrar rotas: {e}")
    import traceback
    traceback.print_exc()

# Arquivos estáticos (avatars) - por último para não interferir nas rotas
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')

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

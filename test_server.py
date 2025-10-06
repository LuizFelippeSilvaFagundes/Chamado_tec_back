#!/usr/bin/env python3
import sys
import traceback

try:
    print("Importando FastAPI...")
    from fastapi import FastAPI
    print("FastAPI importado com sucesso!")
    
    print("Importando dependências do banco...")
    from app.dependencies.database import Base, engine
    print("Dependências do banco importadas com sucesso!")
    
    print("Importando rotas...")
    from app.routes import (
        auth_router,
        user_router,
        ticket_router, 
        tech_router,
        admin_router
    )
    print("Rotas importadas com sucesso!")
    
    print("Criando aplicação FastAPI...")
    app = FastAPI(title="Sistema de Tickets - Prefeitura", version="1.0.0")
    
    print("Configurando CORS...")
    from fastapi.middleware.cors import CORSMiddleware
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    print("Incluindo rotas...")
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(ticket_router)
    app.include_router(tech_router)
    app.include_router(admin_router)
    
    print("Criando tabelas do banco...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
    
    print("Aplicação criada com sucesso!")
    print("Para executar: uvicorn test_server:app --host 127.0.0.1 --port 8000 --reload")
    
except Exception as e:
    print(f"ERRO: {e}")
    print("Traceback completo:")
    traceback.print_exc()
    sys.exit(1)

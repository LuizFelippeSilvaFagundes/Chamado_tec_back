from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from app.routes import (
    auth_router,
    user_router,
    ticket_router, 
    tech_router,
    admin_router
)

# === CRIAÇÃO AUTOMÁTICA DO BANCO E TABELAS ===
def init_db():
    # Cria todas as tabelas se não existirem
    Base.metadata.create_all(bind=engine)

# Inicializa o banco ao iniciar o app
init_db()

app = FastAPI(title="Sistema de Tickets - Prefeitura", version="1.0.0")

# Configuração de CORS
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

# Incluir rotas organizadas por módulos
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(ticket_router)
app.include_router(tech_router)
app.include_router(admin_router)

# Rodar servidor diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

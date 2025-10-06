from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies.database import Base, engine
from pathlib import Path
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
    # Migração simples: garantir coluna avatar_url em users
    with engine.connect() as conn:
        try:
            cols = conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()
            col_names = {c[1] for c in cols}
            if 'avatar_url' not in col_names:
                conn.exec_driver_sql("ALTER TABLE users ADD COLUMN avatar_url VARCHAR")
        except Exception:
            pass                                                     

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

# Arquivos estáticos (avatars)
# Garante que a pasta 'static' exista e usa caminho absoluto para evitar erros
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')

# Rodar servidor diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

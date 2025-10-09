from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Usa PostgreSQL (Supabase) se DATABASE_URL estiver definida, senão usa SQLite local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

# Configuração específica para SQLite (retrocompatibilidade)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Para PostgreSQL (Supabase) não precisa de connect_args especiais
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

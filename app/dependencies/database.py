from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Usa PostgreSQL (Neon/Supabase) se DATABASE_URL estiver definida, senão usa SQLite local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

# Configuração específica para SQLite (retrocompatibilidade)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Para PostgreSQL (Neon/Supabase) com pool de conexões otimizado
    # pool_pre_ping=True verifica conexões antes de usar
    # echo=True para debug (pode remover em produção)
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 10}  # Timeout de 10 segundos
        )
        print(f"✅ Engine do banco de dados criado: {DATABASE_URL[:20]}...")
    except Exception as e:
        print(f"⚠️ AVISO: Erro ao criar engine do banco: {e}")
        # Em produção, não podemos continuar sem banco, mas vamos tentar mesmo assim
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

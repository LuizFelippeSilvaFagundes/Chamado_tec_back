from sqlalchemy import create_engine, text
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
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 5}  # Timeout de 5 segundos
        )
        # Testar conexão imediatamente
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Engine do banco de dados criado e testado")
    except Exception as e:
        print(f"⚠️ AVISO: Erro ao criar engine do banco: {e}")
        import traceback
        traceback.print_exc()
        # Criar engine básico mesmo com erro (para não crashar)
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

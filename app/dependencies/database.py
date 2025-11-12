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
            max_overflow=10
        )
        print(f"✅ Engine do banco de dados criado")
        # Não testar conexão aqui para não travar startup
    except Exception as e:
        print(f"⚠️ AVISO: Erro ao criar engine do banco: {e}")
        # Criar engine básico mesmo com erro (para não crashar)
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 3})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependência para obter sessão do banco de dados"""
    import logging
    logger = logging.getLogger(__name__)
    
    db = SessionLocal()
    try:
        logger.debug("🔌 Sessão do banco de dados criada")
        yield db
    except Exception as e:
        logger.error(f"❌ Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("🔌 Fechando sessão do banco de dados")
        db.close()

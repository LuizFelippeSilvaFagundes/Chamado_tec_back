# -*- coding: utf-8 -*-
"""
Script de configuração inicial do Banco de Dados (Neon/Supabase)
Execute este script após criar o arquivo .env com a URL do banco de dados
"""

import sys
import io

# Configura encoding para UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.dependencies.database import Base, engine, DATABASE_URL
from app.models import User, Ticket, Comment, TicketHistory, RoleEnum
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    print("🔨 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

def create_admin_user():
    """Cria um usuário administrador padrão se não existir"""
    from app.dependencies.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Verifica se já existe um admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if not existing_admin:
            print("👤 Criando usuário administrador padrão...")
            admin = User(
                username="admin",
                email="admin@prefeitura.gov.br",
                hashed_password=pwd_context.hash("admin123"),
                full_name="Administrador do Sistema",
                role=RoleEnum.admin,
                is_active=True,
                is_approved=True
            )
            db.add(admin)
            db.commit()
            print("✅ Usuário admin criado!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        else:
            print("ℹ️  Usuário admin já existe.")
    
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()

def verify_connection():
    """Verifica se a conexão com o banco está funcionando"""
    print("🔍 Verificando conexão com o banco de dados...")
    print(f"📍 URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Local SQLite'}")
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexão estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n⚠️  Verifique se:")
        print("   1. O arquivo .env existe e está configurado corretamente")
        print("   2. A URL do DATABASE_URL está correta")
        print("   3. O projeto Neon/Supabase está ativo")
        return False

def main():
    print("=" * 60)
    print("🚀 CONFIGURAÇÃO DO SUPABASE - Sistema de Tickets")
    print("=" * 60)
    print()
    
    # 1. Verifica conexão
    if not verify_connection():
        return
    
    print()
    
    # 2. Cria tabelas
    create_tables()
    
    print()
    
    # 3. Cria usuário admin
    create_admin_user()
    
    print()
    print("=" * 60)
    print("✨ Configuração concluída com sucesso!")
    print("=" * 60)
    print()
    print("📝 Próximos passos:")
    print("   1. Execute: python main.py (ou python run_server.py)")
    print("   2. Acesse: http://localhost:8000/docs")
    print("   3. Faça login com admin/admin123")
    print("   4. Altere a senha do administrador!")
    print()

if __name__ == "__main__":
    main()


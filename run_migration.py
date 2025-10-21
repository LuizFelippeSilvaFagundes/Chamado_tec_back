#!/usr/bin/env python3
"""
Script para executar a migração do banco de dados
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from alembic.config import Config
from alembic import command

def run_migration():
    """Executa a migração do banco de dados"""
    try:
        # Configurar o alembic
        alembic_cfg = Config(str(project_dir / "alembic.ini"))
        
        # Executar a migração
        print("🔄 Executando migração do banco de dados...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migração executada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao executar migração: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

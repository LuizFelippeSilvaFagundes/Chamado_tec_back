#!/usr/bin/env python3
"""
Script wrapper para executar main.py automaticamente com o ambiente virtual
"""
import sys
import os
from pathlib import Path

# Caminho do projeto
PROJECT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_DIR / "venv" / "bin" / "python"

def main():
    # Verificar se o venv existe
    if not VENV_PYTHON.exists():
        print("❌ Ambiente virtual não encontrado!")
        print("📦 Execute primeiro: python3 -m venv venv")
        print("📦 Depois: pip install -r requirements.txt")
        sys.exit(1)
    
    # Executar main.py usando o Python do venv
    os.chdir(PROJECT_DIR)
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(PROJECT_DIR / "main.py")])

if __name__ == "__main__":
    main()


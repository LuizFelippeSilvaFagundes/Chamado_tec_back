#!/usr/bin/env python3
"""
Script para executar o servidor FastAPI do sistema de tickets da prefeitura
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências do requirements.txt"""
    print("Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def run_server():
    """Executa o servidor FastAPI"""
    print("Iniciando servidor FastAPI...")
    print("Acesse: http://127.0.0.1:8000")
    print("Documentação da API: http://127.0.0.1:8000/docs")
    print("Pressione Ctrl+C para parar o servidor")
    print("-" * 50)
    
    try:
        # Executa o main.py
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")

if __name__ == "__main__":
    print("🚀 Sistema de Tickets - Prefeitura")
    print("=" * 50)
    
    # Verifica se o arquivo main.py existe
    if not os.path.exists("main.py"):
        print("❌ Arquivo main.py não encontrado!")
        sys.exit(1)
    
    # Instala dependências
    if install_requirements():
        # Executa o servidor
        run_server()
    else:
        print("❌ Não foi possível instalar as dependências. Verifique se o Python está instalado corretamente.")
        sys.exit(1)

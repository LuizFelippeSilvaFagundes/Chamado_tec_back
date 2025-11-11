#!/bin/bash
# Script para iniciar o servidor FastAPI no Linux

cd "$(dirname "$0")"

echo "🚀 Iniciando servidor FastAPI..."
echo ""

# Verifica se a porta 8000 está em uso e libera se necessário
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Porta 8000 já está em uso. Encerrando processo anterior..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || pkill -f "python.*main.py" 2>/dev/null
    sleep 2
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Executa o servidor
python main.py


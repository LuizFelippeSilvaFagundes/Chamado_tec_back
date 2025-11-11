# GUIA DE COMANDOS - TERMINAL
# ============================================

# 1. NAVEGAR ATÉ A PASTA DO PROJETO
cd "/home/luiz-felippe/Área de trabalho/projeto_prefeitura/Chamado_tec_back"

# 2. INICIAR O SERVIDOR (escolha uma opção):

# OPÇÃO A - Usar o script (RECOMENDADO):
./start.sh

# OPÇÃO B - Manual passo a passo:
# Primeiro, liberar porta se estiver ocupada:
lsof -ti:8000 | xargs kill -9

# Depois, ativar ambiente virtual e iniciar:
source venv/bin/activate
python main.py

# OPÇÃO C - Tudo em uma linha:
lsof -ti:8000 | xargs kill -9 2>/dev/null; source venv/bin/activate && python main.py

# 3. PARAR O SERVIDOR:
# Pressione Ctrl + C no terminal onde está rodando

# 4. ACESSAR A API:
# Abra no navegador: http://127.0.0.1:8000/docs

# 5. VERIFICAR SE ESTÁ RODANDO:
curl http://127.0.0.1:8000/docs

# 6. VER PROCESSOS NA PORTA 8000:
lsof -i:8000

# 7. MATAR PROCESSO NA PORTA 8000:
lsof -ti:8000 | xargs kill -9


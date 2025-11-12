# Deploy no Render.com - Guia Simples

## Passo 1: Criar conta
1. Acesse: https://render.com
2. Faça login com GitHub
3. Conecte seu repositório

## Passo 2: Criar Web Service
1. Clique em "New" → "Web Service"
2. Conecte o repositório: `Chamado_tec_back`
3. Configure:
   - **Name**: `chamado-tec-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Passo 3: Variáveis de Ambiente
Adicione estas variáveis:
- `DATABASE_URL`: URL do seu banco Neon
- `SECRET_KEY`: qualquer string aleatória (ex: `minha-chave-123`)
- `ENVIRONMENT`: `production`
- `PORT`: deixe vazio (Render define automaticamente)

## Passo 4: Deploy
1. Clique em "Create Web Service"
2. Aguarde o deploy (2-3 minutos)
3. Seu link será: `https://chamado-tec-backend.onrender.com`

## Pronto! 🎉

O Render.com é mais simples e estável que o Railway para este tipo de aplicação.


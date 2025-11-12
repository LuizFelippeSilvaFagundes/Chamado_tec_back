# ✅ Checklist para Deploy no Railway

## 🎯 Status: PRONTO PARA DEPLOY!

Todas as correções foram implementadas e commitadas. Você pode fazer o deploy agora!

---

## 📋 Checklist Final

### **1. Código:**
- [x] Dockerfile configurado corretamente
- [x] railway.json configurado
- [x] Tratamento de erros implementado
- [x] Inicialização do banco corrigida
- [x] Variáveis de ambiente validadas
- [x] Commit e push realizados

### **2. Variáveis de Ambiente no Railway:**

**⚠️ IMPORTANTE:** Configure essas variáveis no Railway antes do deploy:

```
DATABASE_URL=sua-url-do-neon
SECRET_KEY=sua-chave-gerada (openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
ALLOWED_ORIGINS=https://sua-url-frontend.railway.app
```

**⚠️ NÃO configure:**
- `PORT` (Railway define automaticamente)

---

## 🚀 Passo a Passo para Deploy

### **1. No Railway:**

1. **Acesse:** https://railway.app
2. **Selecione seu projeto**
3. **Clique no serviço do backend**

### **2. Configure Variáveis de Ambiente:**

1. **Vá em "Variables"**
2. **Adicione/Verifique cada variável:**

   **DATABASE_URL:**
   - Valor: Sua URL do Neon (ex: `postgresql://user:pass@host/db?sslmode=require`)
   - ⚠️ Copie do seu `.env` local ou do painel do Neon

   **SECRET_KEY:**
   - Valor: Gere uma chave: `openssl rand -hex 32`
   - ⚠️ Deve ser uma string aleatória, NÃO um número

   **ACCESS_TOKEN_EXPIRE_MINUTES:**
   - Valor: `30`
   - ⚠️ Deve ser um NÚMERO, não uma string

   **ALGORITHM:**
   - Valor: `HS256`

   **ENVIRONMENT:**
   - Valor: `production`

   **ALLOWED_ORIGINS:**
   - Valor: URL do frontend (ex: `https://seu-frontend.railway.app`)
   - ⚠️ Configure depois de fazer deploy do frontend
   - ⚠️ Por enquanto, pode deixar vazio ou usar `*` temporariamente

3. **Clique em "Save"**

### **3. Deploy:**

1. **O Railway detecta automaticamente** o push para o repositório
2. **Inicia o build automaticamente**
3. **Aguarde o build completar**
4. **Verifique os logs** para confirmar que iniciou sem erros

### **4. Verificar se Funcionou:**

1. **Acesse os logs do Railway:**
   - Procure por: "✅ Banco de dados inicializado!"
   - Procure por: "Application startup complete"
   - Não deve haver erros críticos

2. **Teste o endpoint `/health`:**
   - Acesse: `https://seu-backend.railway.app/health`
   - Deve retornar JSON com status

3. **Teste o endpoint `/docs`:**
   - Acesse: `https://seu-backend.railway.app/docs`
   - Deve abrir a documentação do FastAPI

---

## 🔍 Verificar se Está Funcionando

### **Endpoint /health:**
```bash
curl https://seu-backend.railway.app/health
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "environment": "production",
  "database": "connected",
  "cors_origins": ["..."]
}
```

### **Endpoint /docs:**
- Acesse no navegador: `https://seu-backend.railway.app/docs`
- Deve abrir a interface Swagger do FastAPI

---

## ⚠️ Problemas Comuns

### **1. "Application failed to respond":**
- Verifique se `DATABASE_URL` está correta
- Verifique se `SECRET_KEY` está configurada
- Verifique os logs para erros específicos

### **2. Erro de conexão com banco:**
- Verifique se `DATABASE_URL` está acessível
- Verifique se as credenciais estão corretas
- Verifique se o Neon permite conexões externas

### **3. Erro de CORS:**
- Configure `ALLOWED_ORIGINS` com a URL do frontend
- Verifique se a URL está correta (sem barra no final)

---

## 🎉 Após Deploy Bem-Sucedido

1. **Copie a URL do backend:**
   - Exemplo: `https://seu-backend.railway.app`

2. **Configure o frontend:**
   - Adicione variável: `VITE_API_URL=https://seu-backend.railway.app`

3. **Teste a aplicação:**
   - Acesse o frontend
   - Teste login, criar ticket, etc.

---

## ✅ Pronto!

**Você pode fazer o deploy agora!**

1. Configure as variáveis de ambiente no Railway
2. Aguarde o build completar
3. Teste os endpoints `/health` e `/docs`
4. Se tudo funcionar, configure o frontend

---

**Boa sorte com o deploy! 🚀**


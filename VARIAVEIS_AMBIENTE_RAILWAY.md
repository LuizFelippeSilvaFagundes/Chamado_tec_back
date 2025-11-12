# 🔧 Configuração de Variáveis de Ambiente no Railway

## ❌ Problema Identificado

O erro ocorre porque a variável `ACCESS_TOKEN_EXPIRE_MINUTES` está recebendo um valor não numérico no Railway.

**Erro:**
```
ValueError: invalid literal for int() with base 10: 'crdos5vhv2b5hulmxg1xtz7g3d8kdv6d'
```

Isso indica que uma `SECRET_KEY` foi configurada no lugar errado, ou há um problema com as variáveis de ambiente.

---

## ✅ Solução Implementada

1. **Adicionado tratamento de erro** ao converter variáveis de ambiente para inteiro
2. **Função helper** `get_int_env()` que trata erros graciosamente
3. **Mensagem de aviso** quando valor inválido é detectado

---

## 📋 Variáveis de Ambiente Necessárias no Railway

### **Backend (Railway):**

```
DATABASE_URL=sua-url-do-neon
SECRET_KEY=sua-chave-gerada (ex: openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
ALLOWED_ORIGINS=https://sua-url-frontend.railway.app
PORT= (automático, não precisa configurar)
```

---

## 🔍 Verificar Variáveis no Railway

1. **Acesse o projeto no Railway**
2. **Vá em Variables** (no serviço do backend)
3. **Verifique cada variável:**

### ✅ **SECRET_KEY:**
- Deve ser uma string aleatória
- Exemplo: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
- **NÃO deve ser um número**

### ✅ **ACCESS_TOKEN_EXPIRE_MINUTES:**
- Deve ser um **número**
- Exemplo: `30`
- **NÃO deve ser uma string como SECRET_KEY**

### ✅ **DATABASE_URL:**
- Deve ser a URL completa do Neon
- Formato: `postgresql://user:password@host/dbname?sslmode=require`

### ✅ **ALGORITHM:**
- Deve ser: `HS256`
- **Não precisa mudar**

### ✅ **ENVIRONMENT:**
- Deve ser: `production`

### ✅ **ALLOWED_ORIGINS:**
- Deve ser a URL do frontend
- Exemplo: `https://seu-frontend.railway.app`

---

## 🚨 Problema Comum

**Erro:** `ACCESS_TOKEN_EXPIRE_MINUTES` recebe valor de `SECRET_KEY`

**Causa:** Variáveis configuradas incorretamente no Railway

**Solução:**
1. Verifique se `SECRET_KEY` e `ACCESS_TOKEN_EXPIRE_MINUTES` estão configuradas corretamente
2. `SECRET_KEY` = string aleatória
3. `ACCESS_TOKEN_EXPIRE_MINUTES` = número (30)

---

## 🔧 Como Corrigir no Railway

1. **Acesse:** Railway Dashboard → Seu Projeto → Backend Service → Variables
2. **Verifique `ACCESS_TOKEN_EXPIRE_MINUTES`:**
   - Deve ser: `30` (número)
   - **NÃO deve ser:** uma string como `crdos5vhv2b5hulmxg1xtz7g3d8kdv6d`
3. **Verifique `SECRET_KEY`:**
   - Deve ser uma string aleatória
   - **NÃO deve ser:** um número
4. **Salve as alterações**
5. **Redeploy** do serviço

---

## 📝 Exemplo Correto

```bash
# ✅ Correto
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ❌ Errado
SECRET_KEY=30
ACCESS_TOKEN_EXPIRE_MINUTES=crdos5vhv2b5hulmxg1xtz7g3d8kdv6d
```

---

## ✅ Após Correção

1. **Salve as variáveis corretas no Railway**
2. **Redeploy** do serviço
3. **Verifique os logs** para confirmar que não há mais erros
4. **Teste o endpoint** `/health` para verificar se está funcionando

---

## 🎉 Pronto!

Com a correção no código, mesmo que haja um valor inválido, o sistema usará o valor padrão (30) e continuará funcionando, mas é importante corrigir as variáveis no Railway para evitar confusão.

---

**Boa sorte! 🚀**


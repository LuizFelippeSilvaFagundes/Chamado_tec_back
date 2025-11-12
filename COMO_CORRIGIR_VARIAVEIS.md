# 🔧 Como Corrigir Variáveis de Ambiente no Railway

## 🚨 Problema

O erro ocorre porque `ACCESS_TOKEN_EXPIRE_MINUTES` está recebendo um valor que não é um número.

**Erro:**
```
ValueError: invalid literal for int() with base 10: 'crdos5vhv2b5hulmxg1xtz7g3d8kdv6d'
```

Isso indica que uma `SECRET_KEY` foi configurada no lugar de `ACCESS_TOKEN_EXPIRE_MINUTES`.

---

## ✅ Solução Rápida

### **1. Acesse o Railway:**
- Vá em: https://railway.app
- Selecione seu projeto
- Clique no serviço do backend
- Vá em **"Variables"**

### **2. Verifique as Variáveis:**

#### ✅ **ACCESS_TOKEN_EXPIRE_MINUTES:**
- **Deve ser:** `30` (número)
- **NÃO deve ser:** uma string como `crdos5vhv2b5hulmxg1xtz7g3d8kdv6d`

#### ✅ **SECRET_KEY:**
- **Deve ser:** uma string aleatória (ex: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)
- **NÃO deve ser:** um número

### **3. Corrija se necessário:**
- Se `ACCESS_TOKEN_EXPIRE_MINUTES` tem um valor de `SECRET_KEY`, **delete e crie novamente** com valor `30`
- Se `SECRET_KEY` está vazia ou incorreta, **adicione uma chave gerada**

### **4. Gere uma SECRET_KEY:**
```bash
openssl rand -hex 32
```

### **5. Salve e Redeploy:**
- Clique em **"Save"**
- O Railway fará redeploy automaticamente

---

## 📋 Variáveis Corretas

```
DATABASE_URL=sua-url-do-neon
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
ALLOWED_ORIGINS=https://sua-url-frontend.railway.app
```

---

## 🔍 Verificar se Está Correto

1. **Acesse os logs do Railway**
2. **Procure por:** `⚠️ AVISO`
3. **Se aparecer:** significa que há um valor inválido, mas o sistema está usando o padrão
4. **Corrija as variáveis** para remover o aviso

---

## ✅ Após Correção

1. **Variáveis corrigidas no Railway**
2. **Redeploy automático**
3. **Servidor inicia sem erros**
4. **Teste o endpoint:** `https://seu-backend.railway.app/health`

---

## 🎉 Pronto!

Com a correção no código, o sistema agora:
- ✅ **Trata valores inválidos** graciosamente
- ✅ **Usa valores padrão** quando necessário
- ✅ **Mostra avisos** nos logs para ajudar a identificar problemas
- ✅ **Continua funcionando** mesmo com valores incorretos (mas é importante corrigir!)

---

**Boa sorte! 🚀**


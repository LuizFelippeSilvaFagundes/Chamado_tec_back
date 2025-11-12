# 🔍 Como Verificar Logs no Railway

## 🚨 Problema: "Application failed to respond"

O build foi bem-sucedido, mas a aplicação não está respondendo. Precisamos verificar os logs do container em execução.

---

## 📋 Passo a Passo para Verificar Logs

### **1. Acessar Logs no Railway:**

1. **Acesse:** https://railway.app
2. **Selecione seu projeto**
3. **Clique no serviço do backend**
4. **Vá em "Logs"** (aba ao lado de "Deployments")
5. **Procure por erros após o build**

### **2. O que procurar nos logs:**

#### ✅ **Logs que indicam sucesso:**
```
🚀 Iniciando servidor...
📍 Ambiente: production
🔌 Porta: 8000 (ou outra)
✅ Banco de dados inicializado!
✅ Servidor iniciado com sucesso!
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

#### ❌ **Logs que indicam erro:**
```
❌ Erro ao iniciar servidor: ...
⚠️ AVISO: Erro ao inicializar banco de dados: ...
Error: ...
Traceback (most recent call last):
```

---

## 🔍 Problemas Comuns

### **1. Erro de Conexão com Banco:**

**Sintomas:**
- Logs mostram erro de conexão
- `DATABASE_URL` incorreta ou inacessível

**Solução:**
- Verifique `DATABASE_URL` no Railway
- Verifique se o Neon permite conexões externas
- Teste a URL localmente

### **2. Erro de Variáveis de Ambiente:**

**Sintomas:**
- Logs mostram erro de variáveis
- `SECRET_KEY` ou outras variáveis faltando

**Solução:**
- Verifique todas as variáveis no Railway
- Certifique-se de que todas estão configuradas

### **3. Erro na Inicialização:**

**Sintomas:**
- Servidor crasha após iniciar
- Erro no startup event

**Solução:**
- Verifique os logs completos
- Procure por erros específicos
- Verifique se todas as dependências estão instaladas

---

## 🔧 Próximos Passos

1. **Verifique os logs no Railway**
2. **Procure por erros específicos**
3. **Compartilhe os logs** para ajudar a resolver

---

## 📋 Checklist

- [ ] Logs do Railway verificados
- [ ] Erros identificados
- [ ] Variáveis de ambiente verificadas
- [ ] `DATABASE_URL` verificada
- [ ] Erros compartilhados (se necessário)

---

**Verifique os logs e compartilhe os erros encontrados!**


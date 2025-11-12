# 🔧 Solução para Erro libpq5/libpq-dev no Railway

## ✅ Problema Resolvido!

O erro ocorre porque o `psycopg2-binary` precisa dos pacotes do sistema `libpq5` e `libpq-dev` para funcionar.

---

## 🎯 Solução Implementada

Criei o arquivo `nixpacks.toml` que configura o Railway para instalar os pacotes necessários automaticamente.

### **Arquivo criado: `nixpacks.toml`**

```toml
[phases.setup]
nixPkgs = ["python312"]

[phases.install]
aptPkgs = ["libpq-dev", "libpq5", "postgresql-client"]
cmds = [
  "pip install --upgrade pip",
  "pip install -r requirements.txt"
]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

---

## 📋 O que fazer agora:

1. **Commit e push das alterações:**
   ```bash
   git add nixpacks.toml railway.json
   git commit -m "fix: adicionar configuração nixpacks para instalar libpq"
   git push
   ```

2. **No Railway:**
   - O Railway detectará automaticamente o `nixpacks.toml`
   - Fará o redeploy automaticamente
   - Os pacotes serão instalados durante o build

3. **Verificar:**
   - O build deve completar sem erros
   - O backend deve iniciar corretamente

---

## 🔍 O que o arquivo faz:

- **`aptPkgs`**: Instala os pacotes do sistema necessários (`libpq-dev`, `libpq5`, `postgresql-client`)
- **`nixPkgs`**: Define o Python 3.12
- **`cmds`**: Instala as dependências Python normalmente
- **`start`**: Comando para iniciar o servidor

---

## ✅ Próximos passos:

1. **Commit e push**
2. **Aguardar redeploy no Railway**
3. **Verificar se funcionou**
4. **Continuar com o deploy do frontend**

---

## 🎉 Pronto!

O erro deve estar resolvido. Se ainda houver problemas, me avise!


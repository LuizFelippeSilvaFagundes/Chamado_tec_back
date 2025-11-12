# 🔧 Solução para Erro "pip: command not found" no Railway

## ✅ Problema Identificado

O Nixpacks está tentando executar `pip` antes do Python estar completamente configurado no ambiente.

---

## 🎯 Solução: Simplificar nixpacks.toml

O Nixpacks detecta automaticamente projetos Python e instala as dependências. Precisamos apenas especificar os pacotes apt necessários.

### **Arquivo `nixpacks.toml` (Simplificado):**

```toml
[providers]
python = "3.12"

[phases.setup]
nixPkgs = ["python312"]

[phases.install]
aptPkgs = ["libpq-dev", "libpq5", "postgresql-client"]
```

### **O que mudou:**

1. ✅ Removido comandos `pip install` customizados
2. ✅ Deixado o Nixpacks instalar dependências automaticamente
3. ✅ Mantidos apenas os pacotes apt necessários
4. ✅ O comando de start está no `railway.json` e `Procfile`

---

## 📋 Arquivos Configurados

### **1. nixpacks.toml:**
- Especifica Python 3.12
- Instala pacotes apt necessários
- Deixa o Nixpacks gerenciar o resto

### **2. railway.json:**
- Comando de start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **3. Procfile:**
- Comando de start alternativo

### **4. runtime.txt:**
- Especifica Python 3.12 (opcional, mas ajuda)

---

## 🚀 Próximos Passos

1. **Commit e push:**
   ```bash
   git add nixpacks.toml railway.json runtime.txt
   git commit -m "fix: simplificar nixpacks.toml para resolver erro pip"
   git push
   ```

2. **No Railway:**
   - O Railway detectará automaticamente o Python
   - Instalará os pacotes apt
   - Instalará as dependências Python automaticamente
   - Iniciará o servidor

---

## ✅ O que deve acontecer agora:

1. ✅ Nixpacks detecta `requirements.txt`
2. ✅ Instala Python 3.12
3. ✅ Instala pacotes apt (`libpq-dev`, `libpq5`, `postgresql-client`)
4. ✅ Instala dependências Python automaticamente
5. ✅ Inicia o servidor com `uvicorn`

---

## 🎉 Pronto!

O erro deve estar resolvido. O Nixpacks agora gerenciará tudo automaticamente!


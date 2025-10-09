# 🚀 Guia Rápido: Configurando Supabase

## ⏱️ Tempo estimado: 10 minutos

---

## 📋 Checklist

- [ ] Criar conta no Supabase
- [ ] Criar projeto
- [ ] Copiar URL de conexão
- [ ] Criar arquivo .env
- [ ] Instalar dependências
- [ ] Executar setup
- [ ] Testar aplicação

---

## 1️⃣ Criar Conta no Supabase (2 min)

1. Acesse: **https://supabase.com**
2. Clique em **"Start your project"**
3. Faça login com **GitHub** (mais rápido)

---

## 2️⃣ Criar Novo Projeto (5 min)

1. Clique em **"New Project"**
2. Preencha:
   ```
   Name: projeto-prefeitura
   Database Password: [ESCOLHA UMA SENHA FORTE E ANOTE!]
   Region: South America (São Paulo)
   ```
3. Clique em **"Create new project"**
4. ⏳ Aguarde ~2 minutos (tome um café ☕)

---

## 3️⃣ Copiar URL de Conexão (1 min)

1. No painel do Supabase, clique no ícone de **⚙️ Settings**
2. Clique em **"Database"** no menu lateral
3. Role até **"Connection String"**
4. Selecione a aba **"URI"**
5. Clique para copiar a URL completa
   - Exemplo: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`
6. ⚠️ **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha que você criou no passo 2

---

## 4️⃣ Configurar Projeto (2 min)

### Windows (PowerShell):

```powershell
# 1. Ativar ambiente virtual
venv\Scripts\Activate.ps1

# 2. Instalar novas dependências
pip install psycopg2-binary python-dotenv

# 3. Criar arquivo .env (copie do exemplo)
Copy-Item env.example .env

# 4. Abrir o .env no notepad
notepad .env
```

### Linux/Mac:

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Instalar novas dependências
pip install psycopg2-binary python-dotenv

# 3. Criar arquivo .env
cp env.example .env

# 4. Editar o .env
nano .env  # ou use seu editor favorito
```

### Editar o arquivo .env:

Cole sua URL do Supabase:

```env
DATABASE_URL=postgresql://postgres:SUA-SENHA@db.xxxxx.supabase.co:5432/postgres
SECRET_KEY=use-uma-chave-super-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

💡 **Dica**: Para gerar uma SECRET_KEY forte, use:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Salve e feche o arquivo.**

---

## 5️⃣ Configurar Banco de Dados (1 min)

Execute o script de setup:

```bash
python setup_supabase.py
```

Você verá:
```
============================================================
🚀 CONFIGURAÇÃO DO SUPABASE - Sistema de Tickets
============================================================

🔍 Verificando conexão com o banco de dados...
📍 URL: db.xxxxx.supabase.co:5432/postgres
✅ Conexão estabelecida com sucesso!

🔨 Criando tabelas no banco de dados...
✅ Tabelas criadas com sucesso!

👤 Criando usuário administrador padrão...
✅ Usuário admin criado!
   Username: admin
   Password: admin123
   ⚠️  IMPORTANTE: Altere a senha após o primeiro login!

============================================================
✨ Configuração concluída com sucesso!
============================================================
```

---

## 6️⃣ Iniciar Servidor (30 seg)

```bash
python main.py
```

Ou use:

```bash
# Windows
start.bat

# Linux/Mac
python run_server.py
```

---

## 7️⃣ Testar (1 min)

1. Abra no navegador: **http://localhost:8000/docs**
2. Faça login:
   - Username: `admin`
   - Password: `admin123`
3. ✅ **Funcionou!** Seus dados agora estão na nuvem! ☁️

---

## 🎉 Ver seus Dados no Supabase

1. Volte para o painel do Supabase
2. Clique em **"Table Editor"** 📊
3. Você verá todas as tabelas:
   - `users` - Todos os usuários
   - `tickets` - Todos os chamados
   - `comments` - Comentários
   - `ticket_history` - Histórico

Agora você pode ver, editar e gerenciar seus dados diretamente no Supabase! 🚀

---

## 🐛 Problemas?

### Erro: "connection refused" ou "connection failed"

1. Verifique se copiou a URL completa do Supabase
2. Verifique se substituiu `[YOUR-PASSWORD]` pela sua senha
3. Verifique se o projeto Supabase está ativo (volte no painel)

### Erro: "No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### Erro: "unable to open database file"

Isso é normal! Você não precisa mais do SQLite. O erro pode aparecer mas será ignorado.

### Arquivo .env não funciona

Certifique-se de que:
1. O arquivo se chama exatamente `.env` (com o ponto na frente)
2. Está na pasta `back/` (raiz do projeto backend)
3. Não tem extensão extra como `.env.txt`

---

## 💡 Dicas Úteis

### Ver SQL das suas tabelas
No Supabase, vá em **SQL Editor** e execute:
```sql
-- Ver todos os usuários
SELECT * FROM users;

-- Ver todos os tickets
SELECT * FROM tickets;

-- Ver tickets com nome do usuário
SELECT t.*, u.full_name 
FROM tickets t 
JOIN users u ON t.user_id = u.id;
```

### Backup dos dados
O Supabase faz backup automático! Mas você pode exportar manualmente:
1. Vá em **Database** → **Backups**
2. Clique em **"Download"**

### Resetar o banco (apagar tudo)
```bash
# No painel Supabase, vá em SQL Editor e execute:
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

# Depois rode novamente:
python setup_supabase.py
```

---

## ✅ Pronto!

Agora seu sistema está usando banco de dados na nuvem! 🎊

**Vantagens:**
- ☁️ Acesse de qualquer computador
- 🔒 Dados sempre salvos
- 📊 Interface visual linda
- 🚀 Performance melhor
- 💾 Backup automático

**Próximos passos:**
1. Altere a senha do admin
2. Crie seus usuários
3. Configure o frontend para apontar para a API

---

Precisa de ajuda? Abre uma issue no GitHub! 🙋‍♂️


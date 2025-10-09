# 🏛️ Backend - Sistema de Chamados da Prefeitura

## 📋 Descrição
Backend em FastAPI para o sistema de chamados da prefeitura, com autenticação JWT e banco de dados PostgreSQL (Supabase) ou SQLite local.

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- pip
- Conta no Supabase (gratuita) - https://supabase.com

### 📦 Configuração do Supabase

1. **Criar projeto no Supabase:**
   - Acesse https://supabase.com e faça login
   - Clique em "New Project"
   - Preencha:
     - **Name**: projeto-prefeitura
     - **Database Password**: Escolha uma senha forte (anote!)
     - **Region**: South America (São Paulo)
   - Aguarde ~2 minutos para o projeto ser criado

2. **Obter URL de Conexão:**
   - No painel do Supabase, vá em **Settings** → **Database**
   - Role até **Connection String** → **URI**
   - Copie a URL (formato: `postgresql://postgres:[SENHA]@db.xxxxx.supabase.co:5432/postgres`)

3. **Configurar arquivo .env:**
   - Copie o arquivo `env.example` para `.env`
   - Cole a URL do Supabase no campo `DATABASE_URL`
   - Gere uma chave secreta forte (use: `openssl rand -hex 32`)

### Instalação Rápida (Windows)
1. **Execute o script de inicialização:**
   ```bash
   start.bat
   ```

### Instalação Manual

1. **Criar ambiente virtual:**
   ```bash
   python -m venv venv
   ```

2. **Ativar ambiente virtual:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar banco de dados (primeira vez):**
   ```bash
   python setup_supabase.py
   ```
   Este script irá:
   - ✅ Verificar conexão com o Supabase
   - ✅ Criar todas as tabelas necessárias
   - ✅ Criar usuário admin padrão (admin/admin123)

5. **Executar o servidor:**
   ```bash
   python main.py
   ```

## 🌐 Endpoints da API

### Autenticação
- `POST /register` - Registrar novo usuário
- `POST /login` - Fazer login
- `GET /me` - Obter perfil do usuário

### Tickets
- `POST /tickets` - Criar novo ticket
- `GET /tickets` - Listar tickets do usuário
- `GET /tickets/{id}` - Obter ticket específico
- `PUT /tickets/{id}` - Atualizar ticket
- `DELETE /tickets/{id}` - Deletar ticket

### Comentários
- `POST /tickets/{id}/comments` - Adicionar comentário
- `GET /tickets/{id}/comments` - Listar comentários
- `DELETE /comments/{id}` - Deletar comentário

## 🗄️ Banco de Dados

### Supabase (PostgreSQL) - Recomendado
- **Tipo:** PostgreSQL hospedado no Supabase
- **Vantagens:**
  - ☁️ Banco de dados na nuvem (seus dados ficam salvos online)
  - 🌍 Acesse de qualquer lugar
  - 📊 Interface visual para ver os dados
  - 💾 500MB grátis
  - 🚀 Mais rápido e robusto que SQLite

### SQLite (Local) - Desenvolvimento
- **Tipo:** SQLite (banco local)
- **Arquivo:** `users.db`
- **Uso:** Apenas se não configurar o Supabase

### Tabelas
- `users` - Usuários do sistema
- `tickets` - Chamados
- `comments` - Comentários dos tickets
- `ticket_history` - Histórico de alterações

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
# Banco de Dados
DATABASE_URL=postgresql://postgres:[SUA-SENHA]@db.xxxxx.supabase.co:5432/postgres

# JWT
SECRET_KEY=sua-chave-secreta-super-forte
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Servidor
- **Porta:** 8000
- **Host:** 127.0.0.1
- **CORS:** Habilitado para localhost:3000 e localhost:5173

## 📝 Estrutura do Projeto
```
back/
├── main.py                  # Aplicação principal FastAPI
├── setup_supabase.py        # Script de configuração do banco
├── env.example              # Exemplo de variáveis de ambiente
├── .env                     # Suas credenciais (criar manualmente)
├── requirements.txt         # Dependências Python
├── start.bat                # Script de inicialização
├── app/
│   ├── models/
│   │   └── models.py        # Modelos do banco de dados
│   ├── schemas/
│   │   └── schemas.py       # Schemas Pydantic
│   ├── controllers/         # Lógica de negócio
│   ├── routes/              # Rotas da API
│   ├── services/            # Serviços
│   └── dependencies/
│       ├── database.py      # Configuração do banco
│       └── auth_dependencies.py  # Autenticação JWT
└── static/
    └── avatars/             # Avatares dos usuários
```

## 🔐 Segurança
- Senhas hasheadas com bcrypt
- Tokens JWT com expiração de 30 minutos
- Validação de usuário em todas as rotas protegidas

## 🧪 Testando a API
Após iniciar o servidor, acesse:
- **Documentação:** http://127.0.0.1:8000/docs
- **API:** http://127.0.0.1:8000

### Usuário Admin Padrão
```
Username: admin
Password: admin123
```
⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## 🐛 Solução de Problemas

### Erro: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Erro: "connection to server failed"
Verifique se:
1. O arquivo `.env` existe e está configurado
2. A URL do DATABASE_URL está correta (inclui a senha)
3. Seu projeto Supabase está ativo

### Erro: "Failed to create tables"
Execute novamente o script de configuração:
```bash
python setup_supabase.py
```

## 🔄 Migrando de SQLite para Supabase

Se você já tem dados no SQLite local:
1. Configure o Supabase normalmente
2. Execute `python setup_supabase.py` para criar as tabelas
3. Os dados antigos do SQLite não serão migrados automaticamente
4. Você precisará recriar usuários e tickets no novo banco

## 💡 Dicas

- 🔍 **Ver dados**: Acesse o painel do Supabase → Table Editor
- 📊 **Queries SQL**: Use o SQL Editor no Supabase
- 🔒 **Backup**: O Supabase faz backup automático dos dados
- 🌐 **Acesso remoto**: Seu banco está na nuvem, acesse de qualquer lugar

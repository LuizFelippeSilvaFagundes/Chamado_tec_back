# 🏛️ Backend - Sistema de Chamados da Prefeitura

## 📋 Descrição
Backend em FastAPI para o sistema de chamados da prefeitura, com autenticação JWT e banco de dados SQLite.

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- pip

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
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar o servidor:**
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
- **Tipo:** SQLite
- **Arquivo:** `users.db`
- **Tabelas:** `users`, `tickets`, `comments`

## 🔧 Configuração
- **Porta:** 8000
- **Host:** 127.0.0.1
- **CORS:** Habilitado para localhost:3000 e localhost:5173

## 📝 Estrutura do Projeto
```
back/
├── main.py          # Aplicação principal FastAPI
├── models.py        # Modelos do banco de dados
├── schemas.py       # Schemas Pydantic
├── crud.py          # Operações CRUD
├── auth.py          # Autenticação JWT
├── database.py      # Configuração do banco
├── requirements.txt # Dependências Python
└── start.bat        # Script de inicialização
```

## 🔐 Segurança
- Senhas hasheadas com bcrypt
- Tokens JWT com expiração de 30 minutos
- Validação de usuário em todas as rotas protegidas

## 🧪 Testando a API
Após iniciar o servidor, acesse:
- **Documentação:** http://127.0.0.1:8000/docs
- **API:** http://127.0.0.1:8000

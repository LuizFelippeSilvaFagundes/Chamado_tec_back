# 🚀 Guia de Deploy - Backend (FastAPI)

## 📋 Pré-requisitos

- Python 3.12+
- PostgreSQL (Neon, Supabase, ou servidor próprio)
- Variáveis de ambiente configuradas
- CORS configurado para produção

---

## 🔧 Configuração para Produção

### **1. Configurar Variáveis de Ambiente**

Crie um arquivo `.env` na raiz do backend:

```bash
# .env (produção)
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
SECRET_KEY=sua-chave-secreta-super-forte-aqui-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Domínios permitidos (separados por vírgula)
ALLOWED_ORIGINS=https://seu-frontend.com,https://www.seu-frontend.com

# Ambiente
ENVIRONMENT=production
```

**Gerar SECRET_KEY:**
```bash
openssl rand -hex 32
```

---

### **2. Atualizar CORS no main.py**

O CORS atual permite `"*"` (todos os origens), o que não é seguro para produção.

**Atualize `main.py`:**

```python
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# Para desenvolvimento, adicionar localhost
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Não usar "*" em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### **3. Configurar Banco de Dados**

#### **Opção 1: Neon (PostgreSQL na Nuvem)**

1. Crie uma conta em https://neon.tech
2. Crie um novo projeto
3. Copie a connection string
4. Adicione no `.env`:
   ```
   DATABASE_URL=postgresql://user:password@ep-xxxxx-pooler.region.aws.neon.tech/dbname?sslmode=require
   ```

#### **Opção 2: Supabase**

1. Crie uma conta em https://supabase.com
2. Crie um novo projeto
3. Vá em "Settings" → "Database"
4. Copie a connection string
5. Adicione no `.env`

#### **Opção 3: Servidor Próprio**

1. Instale PostgreSQL no servidor
2. Crie um banco de dados
3. Adicione no `.env`:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

---

## 🌐 Deploy do Backend

### **Opção 1: Railway (Recomendado)**

#### Vantagens:
- ✅ Grátis para começar
- ✅ PostgreSQL incluído
- ✅ HTTPS automático
- ✅ Deploy automático via Git
- ✅ Variáveis de ambiente fáceis

#### Passo a Passo:

1. **Instalar Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Fazer login:**
```bash
railway login
```

3. **Inicializar projeto:**
```bash
cd "/home/luiz-felippe/Área de trabalho/projeto_prefeitura/Chamado_tec_back"
railway init
```

4. **Adicionar PostgreSQL:**
```bash
railway add postgresql
```

5. **Configurar variáveis de ambiente:**
```bash
railway variables set SECRET_KEY=sua-chave-secreta
railway variables set ALLOWED_ORIGINS=https://seu-frontend.com
railway variables set ENVIRONMENT=production
```

6. **Deploy:**
```bash
railway up
```

7. **Configurar comando de start:**
   - No dashboard da Railway, vá em "Settings" → "Start Command"
   - Adicione: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

### **Opção 2: Render**

#### Vantagens:
- ✅ Grátis para começar
- ✅ PostgreSQL incluído
- ✅ HTTPS automático
- ✅ Deploy automático via Git

#### Passo a Passo:

1. Acesse https://render.com
2. Crie uma nova "Web Service"
3. Conecte o repositório do backend
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Adicione variáveis de ambiente:
   - `DATABASE_URL` (Render fornece PostgreSQL)
   - `SECRET_KEY`
   - `ALLOWED_ORIGINS`
   - `ENVIRONMENT=production`

---

### **Opção 3: Servidor VPS (DigitalOcean, AWS EC2, etc.)**

#### Passo a Passo:

1. **Instalar dependências:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql
```

2. **Configurar PostgreSQL:**
```bash
sudo -u postgres createdb chamados_db
sudo -u postgres createuser chamados_user
sudo -u postgres psql -c "ALTER USER chamados_user WITH PASSWORD 'sua-senha';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE chamados_db TO chamados_user;"
```

3. **Configurar aplicação:**
```bash
cd /var/www/chamados-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configurar systemd service:**
```bash
sudo nano /etc/systemd/system/chamados-backend.service
```

```ini
[Unit]
Description=Chamados Backend API
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/chamados-backend
Environment="PATH=/var/www/chamados-backend/venv/bin"
EnvironmentFile=/var/www/chamados-backend/.env
ExecStart=/var/www/chamados-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Iniciar serviço:**
```bash
sudo systemctl daemon-reload
sudo systemctl start chamados-backend
sudo systemctl enable chamados-backend
```

6. **Configurar Nginx:**
```bash
sudo nano /etc/nginx/sites-available/chamados-api
```

```nginx
server {
    listen 80;
    server_name api.chamados.prefeitura.gov.br;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/chamados-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Configurar SSL (Let's Encrypt):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.chamados.prefeitura.gov.br
```

---

## 🔒 Segurança

### **1. CORS Configurado Corretamente**

✅ **NUNCA use `"*"` em produção!**

Configure apenas os domínios do frontend:
```python
ALLOWED_ORIGINS=https://seu-frontend.com,https://www.seu-frontend.com
```

### **2. HTTPS**

- ✅ Sempre use HTTPS em produção
- ✅ Railway/Render fornecem HTTPS automático
- ✅ Em VPS, use Let's Encrypt (gratuito)

### **3. Variáveis de Ambiente**

- ✅ Nunca commite arquivos `.env`
- ✅ Use variáveis de ambiente na plataforma de deploy
- ✅ SECRET_KEY deve ser forte e único

### **4. Banco de Dados**

- ✅ Use SSL para conexão com banco de dados
- ✅ Use senhas fortes
- ✅ Faça backups regulares

---

## 🧪 Testar o Deploy

### **1. Verificar se o backend está rodando:**

```bash
curl https://seu-backend.com/docs
```

Deve retornar a documentação Swagger.

### **2. Testar CORS:**

Abra o console do navegador e teste uma requisição:
```javascript
fetch('https://seu-backend.com/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'test', password: 'test' })
})
```

Se houver erro de CORS, verifique `ALLOWED_ORIGINS`.

### **3. Testar Endpoints:**

- ✅ `GET /docs` - Documentação Swagger
- ✅ `POST /login` - Login
- ✅ `GET /tickets` - Listar tickets (com autenticação)

---

## 📊 Monitoramento

### **1. Logs**

- **Railway:** Dashboard → Deployments → Logs
- **Render:** Dashboard → Logs
- **VPS:** `sudo journalctl -u chamados-backend -f`

### **2. Health Check**

Adicione um endpoint de health check:

```python
@app.get("/health")
def health_check():
    return {"status": "ok", "environment": os.getenv("ENVIRONMENT", "development")}
```

---

## 🔄 Atualizar CORS no Código

Vou criar um arquivo atualizado do `main.py` com CORS configurável via variável de ambiente:

```python
# Adicionar no início do arquivo
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de CORS
def get_allowed_origins():
    """Retorna lista de origens permitidas baseada em variáveis de ambiente"""
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    
    if env_origins:
        # Separar por vírgula e remover espaços
        origins = [origin.strip() for origin in env_origins.split(",")]
    else:
        origins = []
    
    # Em desenvolvimento, adicionar localhost
    if os.getenv("ENVIRONMENT") != "production":
        origins.extend([
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ])
    
    return origins if origins else ["*"]  # Fallback para desenvolvimento

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ✅ Checklist de Deploy

### **Configuração:**
- [ ] Variáveis de ambiente configuradas
- [ ] CORS configurado para domínios específicos
- [ ] SECRET_KEY gerado e configurado
- [ ] Banco de dados configurado
- [ ] `.env` não está no Git (`.gitignore`)

### **Deploy:**
- [ ] Backend rodando em produção
- [ ] HTTPS configurado
- [ ] Health check funcionando
- [ ] Logs configurados

### **Testes:**
- [ ] API respondendo (`/docs`)
- [ ] CORS funcionando
- [ ] Login funcionando
- [ ] Endpoints protegidos funcionando

---

## 🐛 Troubleshooting

### **Problema: CORS Error**

**Solução:**
1. Verifique `ALLOWED_ORIGINS` no `.env`
2. Verifique se o domínio do frontend está na lista
3. Reinicie o servidor após mudar variáveis

### **Problema: Database Connection Error**

**Solução:**
1. Verifique `DATABASE_URL` no `.env`
2. Verifique se o banco de dados está acessível
3. Verifique se as credenciais estão corretas

### **Problema: 500 Internal Server Error**

**Solução:**
1. Verifique os logs do servidor
2. Verifique se todas as variáveis de ambiente estão configuradas
3. Verifique se o banco de dados está funcionando

---

## 🎉 Pronto!

Após seguir este guia, seu backend estará rodando em produção!

**Próximos Passos:**
1. Configure o frontend para usar a URL do backend em produção
2. Teste todas as funcionalidades
3. Configure monitoramento
4. Configure backups do banco de dados

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do servidor
2. Verifique as variáveis de ambiente
3. Verifique a configuração de CORS
4. Verifique a conexão com o banco de dados


# Arquitetura MVC - Sistema de Tickets

## 📁 Estrutura de Diretórios

```
/workspace/
├── app/                          # Aplicação principal organizada em MVC
│   ├── controllers/              # Controllers - Lógica de controle
│   │   ├── __init__.py
│   │   ├── auth_controller.py    # Controlador de autenticação
│   │   ├── user_controller.py    # Controlador de usuários
│   │   ├── ticket_controller.py  # Controlador de tickets
│   │   ├── tech_controller.py    # Controlador de técnicos
│   │   └── admin_controller.py   # Controlador de administradores
│   │
│   ├── models/                   # Models - Modelos de dados
│   │   ├── __init__.py
│   │   └── models.py            # Definições das entidades do banco
│   │
│   ├── services/                 # Services - Lógica de negócio
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Serviços de autenticação
│   │   ├── user_service.py      # Serviços de usuários
│   │   └── ticket_service.py    # Serviços de tickets
│   │
│   ├── routes/                   # Routes - Definição das rotas
│   │   ├── __init__.py
│   │   ├── auth_routes.py       # Rotas de autenticação
│   │   ├── user_routes.py       # Rotas de usuários
│   │   ├── ticket_routes.py     # Rotas de tickets
│   │   ├── tech_routes.py       # Rotas de técnicos
│   │   └── admin_routes.py      # Rotas de administradores
│   │
│   └── dependencies/             # Dependencies - Dependências compartilhadas
│       ├── __init__.py
│       ├── database.py          # Dependência do banco de dados
│       └── auth_dependencies.py # Dependências de autenticação
│
├── main.py                      # Ponto de entrada da aplicação
├── database.py                  # Configuração do banco de dados
├── schemas.py                   # Schemas Pydantic (DTOs)
├── auth.py                      # [LEGADO] Mantido para compatibilidade
├── crud.py                      # [LEGADO] Mantido para compatibilidade
├── models.py                    # [LEGADO] Mantido para compatibilidade
└── requirements.txt             # Dependências do projeto
```

## 🏗️ Arquitetura MVC

### **Models (Modelos)**
- **Localização**: `app/models/`
- **Responsabilidade**: Definir a estrutura dos dados e entidades do banco
- **Conteúdo**:
  - Classes SQLAlchemy (User, Ticket, Comment, TicketHistory)
  - Enums (PriorityEnum, StatusEnum, RoleEnum)
  - Relacionamentos entre entidades

### **Views (Rotas)**
- **Localização**: `app/routes/`
- **Responsabilidade**: Definir endpoints da API e validação de entrada
- **Organização por domínio**:
  - `auth_routes.py` - Login, registro, autenticação
  - `user_routes.py` - Perfil de usuário
  - `ticket_routes.py` - CRUD de tickets
  - `tech_routes.py` - Funcionalidades específicas de técnicos
  - `admin_routes.py` - Funcionalidades administrativas

### **Controllers (Controladores)**
- **Localização**: `app/controllers/`
- **Responsabilidade**: Orquestrar chamadas entre Services e Routes
- **Características**:
  - Recebem dados das Routes
  - Chamam Services para lógica de negócio
  - Tratam exceções específicas
  - Retornam responses padronizados

### **Services (Serviços)**
- **Localização**: `app/services/`
- **Responsabilidade**: Implementar toda a lógica de negócio
- **Benefícios**:
  - Reutilizáveis em diferentes contexts
  - Isolam regras de negócio
  - Facilitam testes unitários
  - Centralizam operações complexas

### **Dependencies (Dependências)**
- **Localização**: `app/dependencies/`
- **Responsabilidade**: Prover dependências compartilhadas
- **Conteúdo**:
  - Sessões de banco de dados
  - Autenticação e autorização
  - Validações de acesso

## 📊 Fluxo de Dados

```
HTTP Request → Route → Controller → Service → Model → Database
                ↓         ↓          ↓        ↓
HTTP Response ← Route ← Controller ← Service ← Model ← Database
```

### Exemplo Prático:

1. **Route** (`POST /tickets`) recebe dados do usuário
2. **Controller** (`TicketController.create_ticket`) valida e organiza dados
3. **Service** (`TicketService.create_ticket`) aplica regras de negócio
4. **Model** (`Ticket`) define estrutura para salvar no banco
5. **Response** retorna ticket criado via Controller → Route

## 🔧 Vantagens da Nova Arquitetura

### ✅ **Organização**
- Código bem estruturado e fácil de navegar
- Responsabilidades claramente definidas
- Arquivos menores e mais focados

### ✅ **Manutenibilidade**
- Mudanças isoladas em camadas específicas
- Facilita debugging e correções
- Reutilização de código

### ✅ **Escalabilidade**
- Fácil adicionar novos recursos
- Estrutura suporta crescimento da aplicação
- Separação permite trabalho em equipe

### ✅ **Testabilidade**
- Services podem ser testados independentemente
- Mock de dependências é mais simples
- Testes unitários mais granulares

## 🚀 Como Usar

### Executar a aplicação:
```bash
cd /workspace
python main.py
```

### Estrutura de uma nova funcionalidade:

1. **Definir modelo** em `app/models/models.py`
2. **Criar service** em `app/services/`
3. **Implementar controller** em `app/controllers/`
4. **Definir rotas** em `app/routes/`
5. **Registrar router** em `main.py`

### Exemplo - Nova funcionalidade "Relatórios":

```python
# 1. app/services/report_service.py
class ReportService:
    @staticmethod
    def generate_monthly_report(db: Session):
        # Lógica do relatório
        pass

# 2. app/controllers/report_controller.py
class ReportController:
    @staticmethod
    def get_monthly_report(db: Session):
        return ReportService.generate_monthly_report(db)

# 3. app/routes/report_routes.py
@router.get("/monthly")
def get_monthly_report(db: Session = Depends(get_db)):
    return ReportController.get_monthly_report(db)

# 4. main.py
from app.routes.report_routes import router as report_router
app.include_router(report_router, prefix="/reports")
```

## 📝 Migrations

Os arquivos legados (`crud.py`, `auth.py`, `models.py`) foram mantidos para compatibilidade durante a transição. Eles podem ser removidos gradualmente conforme a aplicação for testada e validada.

## 🎯 Próximos Passos

1. ✅ Estrutura MVC implementada
2. ✅ Testes de sintaxe executados  
3. 🔄 Testes funcionais da API
4. 🔄 Migração completa dos arquivos legados
5. 🔄 Implementação de testes unitários
6. 🔄 Documentação automática com Swagger
from database import Base, engine
from models import User, Ticket, Comment

# Cria todas as tabelas definidas nos modelos
Base.metadata.create_all(bind=engine)   

print("Banco de dados criado com sucesso! 🚀")

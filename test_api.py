#!/usr/bin/env python3
"""
Script de teste para verificar se a API está funcionando
Execute após iniciar o servidor: python test_api.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Testa se o servidor está rodando"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            return True
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando na porta 8000")
        return False

def test_register():
    """Testa o endpoint de registro"""
    print("\n🧪 Testando registro de usuário...")
    
    user_data = {
        "username": "teste_user",
        "email": "teste@exemplo.com",
        "full_name": "Usuário de Teste",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        if response.status_code == 201:
            print("✅ Usuário registrado com sucesso!")
            return True
        else:
            print(f"❌ Erro no registro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_login():
    """Testa o endpoint de login"""
    print("\n🧪 Testando login...")
    
    login_data = {
        "username": "teste_user",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("✅ Login realizado com sucesso!")
                print(f"   Token: {token[:20]}...")
                return token
            else:
                print("❌ Token não encontrado na resposta")
                return None
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def test_create_ticket(token):
    """Testa a criação de um ticket"""
    print("\n🧪 Testando criação de ticket...")
    
    ticket_data = {
        "title": "Teste de Ticket",
        "description": "Este é um ticket de teste para verificar a API",
        "problem_type": "TI / Computador",
        "location": "Setor de Teste",
        "priority": "medium"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/tickets", json=ticket_data, headers=headers)
        if response.status_code == 201:
            print("✅ Ticket criado com sucesso!")
            return True
        else:
            print(f"❌ Erro na criação do ticket: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_get_tickets(token):
    """Testa a listagem de tickets"""
    print("\n🧪 Testando listagem de tickets...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/tickets", headers=headers)
        if response.status_code == 200:
            tickets = response.json()
            print(f"✅ Tickets listados com sucesso! Total: {len(tickets)}")
            return True
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da API...")
    print("=" * 50)
    
    # Teste 1: Verificar se o servidor está rodando
    if not test_health():
        return
    
    # Teste 2: Registrar usuário
    if not test_register():
        print("⚠️  Usuário pode já existir, continuando...")
    
    # Teste 3: Fazer login
    token = test_login()
    if not token:
        print("❌ Não foi possível fazer login. Testes interrompidos.")
        return
    
    # Teste 4: Criar ticket
    test_create_ticket(token)
    
    # Teste 5: Listar tickets
    test_get_tickets(token)
    
    print("\n" + "=" * 50)
    print("🎉 Testes concluídos!")
    print("📖 Acesse http://127.0.0.1:8000/docs para ver a documentação da API")

if __name__ == "__main__":
    main()

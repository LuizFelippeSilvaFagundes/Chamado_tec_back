@echo off
echo Iniciando o Backend da Prefeitura...
echo.

REM Verificar se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8+ e tente novamente.
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo Instalando dependencias...
pip install -r requirements.txt

REM Iniciar o servidor
echo.
echo Iniciando servidor na porta 8000...
echo Acesse: http://127.0.0.1:8000
echo.
python main.py

pause

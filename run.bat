@echo off
echo ========================================
echo ARQV30 Enhanced - Iniciando Aplicacao
echo ========================================
echo.

REM Verificar se estamos no diretorio correto
if not exist "src" (
    echo ERRO: Diretorio 'src' nao encontrado!
    echo Execute este script a partir da raiz do projeto
    echo.
    pause
    exit /b 1
)

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Execute install.bat primeiro para instalar dependencias
    echo.
    pause
    exit /b 1
)

REM Verificar se arquivo .env existe
if not exist ".env" (
    echo AVISO: Arquivo .env nao encontrado!
    echo Execute install.bat primeiro para criar configuracao
    echo.
    pause
    exit /b 1
)

echo ✓ Verificacoes iniciais concluidas
echo.

REM Definir variaveis de ambiente
set FLASK_APP=src/run.py
set FLASK_ENV=development
set PYTHONPATH=%CD%

echo Carregando configuracoes...
echo ✓ FLASK_APP: %FLASK_APP%
echo ✓ FLASK_ENV: %FLASK_ENV%
echo ✓ PYTHONPATH: %PYTHONPATH%
echo.

REM Verificar dependencias criticas
echo Verificando dependencias criticas...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ERRO: Flask nao instalado!
    echo Execute install.bat primeiro
    pause
    exit /b 1
)

python -c "import google.generativeai" 2>nul
if errorlevel 1 (
    echo AVISO: Google Generative AI nao instalado
    echo Algumas funcionalidades podem nao funcionar
)

python -c "import supabase" 2>nul
if errorlevel 1 (
    echo AVISO: Supabase nao instalado
    echo Banco de dados pode nao funcionar
)

echo ✓ Dependencias verificadas
echo.

echo Iniciando servidor Flask...
echo.
echo ========================================
echo Servidor rodando em: http://localhost:5000
echo ========================================
echo.
echo Para parar o servidor, pressione Ctrl+C
echo.

REM Aguardar um momento e abrir navegador
timeout /t 3 /nobreak >nul
start http://localhost:5000

REM Iniciar aplicacao Flask
cd src
python run.py

REM Se chegou aqui, o servidor foi parado
echo.
echo ========================================
echo Servidor parado
echo ========================================
echo.
pause


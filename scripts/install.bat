@echo off
echo ========================================
echo ARQV30 Enhanced - Script de Instalacao
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.11+ de https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
python --version

REM Verificar se pip esta disponivel
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: pip nao encontrado!
    echo Por favor, reinstale Python com pip incluido
    echo.
    pause
    exit /b 1
)

echo ✓ pip encontrado
pip --version

echo.
echo Instalando dependencias...
echo.

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias principais
echo.
echo Instalando dependencias principais...
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install supabase==1.0.4
pip install google-generativeai==0.3.2
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install Werkzeug==2.3.7

REM Instalar dependencias para PDF
echo.
echo Instalando dependencias para PDF...
pip install reportlab==4.0.4
pip install fpdf2==2.7.6
pip install weasyprint==60.1

REM Instalar dependencias para processamento de dados (versoes compatíveis com Python 3.13)
echo.
echo Instalando dependencias para dados...
pip install Pillow>=10.2.0
pip install pandas>=2.2.0
pip install openpyxl>=3.1.2

REM Instalar dependencias para documentos
echo.
echo Instalando dependencias para documentos...
pip install python-docx>=0.8.11
pip install PyPDF2>=3.0.1
pip install pdfplumber>=0.10.0

REM Instalar dependencias para web scraping (sem lxml por problemas de compilacao)
echo.
echo Instalando dependencias para web...
pip install markdown>=3.5.1
pip install beautifulsoup4>=4.12.2
echo AVISO: lxml foi removido devido a problemas de compatibilidade com Python 3.13

REM Instalar dependencias opcionais para WebSailor
echo.
echo Instalando dependencias opcionais para WebSailor...
pip install openai
pip install tiktoken
pip install transformers
pip install torch --index-url https://download.pytorch.org/whl/cpu

REM Instalar servidor web para producao
echo.
echo Instalando servidor web...
pip install gunicorn==21.2.0

echo.
echo ========================================
echo Instalacao concluida!
echo ========================================
echo.

REM Verificar instalacao
echo Verificando instalacao...
python -c "import flask; print('✓ Flask:', flask.__version__)"
python -c "import google.generativeai; print('✓ Google Generative AI instalado')"
python -c "import supabase; print('✓ Supabase instalado')"
python -c "import pandas; print('✓ Pandas:', pandas.__version__)"
python -c "import requests; print('✓ Requests:', requests.__version__)"

echo.
echo Proximos passos:
echo 1. Configure o arquivo .env com suas chaves de API
echo 2. Execute run.bat para iniciar o aplicativo
echo 3. Acesse http://localhost:5000 no navegador
echo.

REM Verificar se arquivo .env existe
if not exist ".env" (
    echo ATENCAO: Arquivo .env nao encontrado!
    echo Criando arquivo .env de exemplo...
    echo.
    
    echo # ARQV30 Enhanced - Configuracao> .env
    echo # Configure suas chaves de API abaixo>> .env
    echo.>> .env
    echo CORS_ORIGINS=*>> .env
    echo DATABASE_URL=postgresql://postgres.albyamqjdopihijsderu:[9pfVX8TLcxXubcVv]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres>> .env
    echo DEEPSEEK_API_KEY=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>> .env
    echo FLASK_ENV=development>> .env
    echo GEMINI_API_KEY=AIzaSyBtLYVXxG61tu0CZ4uoLcO8pTWZuGteUFc>> .env
    echo PYTHON_VERSION=3.11.0>> .env
    echo SECRET_KEY="FDGD851F8DGhgfhgf_fdsfewn543534==//ddfsehjkj$">> .env
    echo SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFsYnlhbXFqZG9waWhpanNkZXJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MTgzMTYsImV4cCI6MjA2Njk5NDMxNn0.n0fjjyDF7LZYa6MD2ZZ5tUVjEieNDtb_rbvfjNHS_Rg>> .env
    echo SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFsYnlhbXFqZG9waWhpanNkZXJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTQxODMxNiwiZXhwIjoyMDY2OTk0MzE2fQ.muvh9Xxvb2e30d4fwiO8m2cL5x5KI5-VHO0bNd9F4hg>> .env
    echo SUPABASE_URL=https://albyamqjdopihijsderu.supabase.co>> .env
    echo.>> .env
    echo # Configuracoes opcionais para WebSailor>> .env
    echo # GOOGLE_SEARCH_KEY=sua_chave_google_search>> .env
    echo # JINA_API_KEY=sua_chave_jina>> .env
    echo # WEBSAILOR_ENABLED=true>> .env
    
    echo ✓ Arquivo .env criado com configuracoes padrao
    echo   Edite o arquivo .env se necessario
)

echo.
echo Instalacao completa! Execute run.bat para iniciar.
echo.
pause


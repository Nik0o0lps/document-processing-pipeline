@echo off
REM Script de instalação automatizada para Windows

echo ============================================
echo  Pipeline de Processamento de Documentos
echo  Script de Instalacao Automatizada
echo ============================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ de https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python encontrado

REM Cria ambiente virtual
echo.
echo [1/4] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual
    pause
    exit /b 1
)
echo [OK] Ambiente virtual criado

REM Ativa ambiente virtual
echo.
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo [OK] Ambiente ativado

REM Instala dependências
echo.
echo [3/4] Instalando dependencias...
echo Isso pode levar alguns minutos...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

REM Cria arquivo .env se não existir
echo.
echo [4/4] Configurando ambiente...
if not exist .env (
    copy .env.example .env
    echo [AVISO] Arquivo .env criado. EDITE-O com sua OpenAI API key!
) else (
    echo [OK] Arquivo .env ja existe
)

REM Cria diretorio de output
if not exist output mkdir output

echo.
echo ============================================
echo  INSTALACAO CONCLUIDA!
echo ============================================
echo.
echo Proximos passos:
echo 1. Edite o arquivo .env com sua OpenAI API key
echo 2. Coloque seus PDFs na pasta Documentos_Internos/
echo 3. Execute: python main.py
echo.
echo Para testar um documento:
echo   python test_single.py Documentos_Internos/arquivo.pdf
echo.
pause

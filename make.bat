@echo off
REM Script batch para Windows - equivalente ao Makefile
REM Uso: make.bat <comando>

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-dev" goto install-dev
if "%1"=="test" goto test
if "%1"=="test-cov" goto test-cov
if "%1"=="test-fast" goto test-fast
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="clean" goto clean
if "%1"=="run" goto run
if "%1"=="run-debug" goto run-debug
if "%1"=="check-env" goto check-env
if "%1"=="validate" goto validate
if "%1"=="ci" goto ci
if "%1"=="stats" goto stats
echo Comando desconhecido: %1
goto help

:help
echo Document Processing Pipeline - Comandos Disponiveis:
echo.
echo   install         Instala dependencias de producao
echo   install-dev     Instala dependencias de desenvolvimento
echo   test            Executa testes unitarios
echo   test-cov        Executa testes com cobertura
echo   test-fast       Executa apenas testes rapidos (nao slow)
echo   lint            Verifica qualidade do codigo
echo   format          Formata codigo automaticamente
echo   clean           Remove arquivos temporarios e cache
echo   run             Executa o pipeline
echo   run-debug       Executa com log detalhado
echo   check-env       Verifica se .env esta configurado
echo   validate        Validacao completa (lint + tests)
echo   ci              Simula pipeline CI localmente
echo   stats           Mostra estatisticas do projeto
echo.
goto end

:install
echo Instalando dependencias de producao...
python -m pip install -r requirements.txt
goto end

:install-dev
echo Instalando dependencias de desenvolvimento...
python -m pip install -r requirements.txt
python -m pip install black isort flake8 pytest pytest-cov pytest-mock
goto end

:test
echo Executando testes...
python -m pytest tests/ -v
goto end

:test-cov
echo Executando testes com cobertura...
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
echo Relatorio HTML gerado em htmlcov/index.html
goto end

:test-fast
echo Executando testes rapidos...
python -m pytest tests/ -v -m "not slow"
goto end

:lint
echo Verificando qualidade do codigo...
python -m flake8 src tests --max-line-length=127 --extend-ignore=E203,W503
python -m black --check src tests
python -m isort --check-only src tests
goto end

:format
echo Formatando codigo...
python -m black src tests
python -m isort src tests
echo Codigo formatado com sucesso!
goto end

:clean
echo Limpando arquivos temporarios...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
if exist .coverage del /q .coverage
if exist htmlcov rd /s /q htmlcov
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo Limpeza concluida!
goto end

:run
echo Executando pipeline...
python main.py
goto end

:run-debug
echo Executando com log detalhado...
python main.py --log-level DEBUG
goto end

:check-env
echo Verificando configuracao .env...
if not exist .env (
    echo [ERRO] Arquivo .env nao encontrado!
    echo        Copie .env.example para .env e configure suas chaves.
    goto end
)
echo [OK] Arquivo .env encontrado
findstr /C:"GROQ_API_KEY=gsk-" .env >nul 2>&1
if %errorlevel%==0 (
    echo [OK] GROQ_API_KEY configurada
) else (
    echo [AVISO] GROQ_API_KEY nao configurada
)
findstr /C:"OPENAI_API_KEY=sk-" .env >nul 2>&1
if %errorlevel%==0 (
    echo [OK] OPENAI_API_KEY configurada
) else (
    echo [AVISO] OPENAI_API_KEY nao configurada
)
goto end

:validate
echo Executando validacao completa...
call :lint
if %errorlevel% neq 0 goto end
call :test
if %errorlevel% neq 0 goto end
echo [OK] Validacao completa aprovada!
goto end

:ci
echo Simulando pipeline CI localmente...
call :install-dev
if %errorlevel% neq 0 goto end
call :validate
if %errorlevel% neq 0 goto end
echo [OK] CI pipeline executada com sucesso!
goto end

:stats
echo Estatisticas do Projeto:
echo.
echo Linhas de codigo fonte:
powershell -Command "(Get-ChildItem -Path src -Filter *.py -Recurse | Get-Content | Measure-Object -Line).Lines"
echo.
echo Linhas de teste:
powershell -Command "(Get-ChildItem -Path tests -Filter *.py -Recurse | Get-Content | Measure-Object -Line).Lines"
echo.
echo Arquivos Python:
powershell -Command "(Get-ChildItem -Path src,tests -Filter *.py -Recurse | Measure-Object).Count"
goto end

:end

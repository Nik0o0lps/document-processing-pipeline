# Windows Setup Guide

Este guia é para usuários Windows que precisam executar os comandos do projeto.

## Problema: `make` não funciona no Windows

O comando `make` é uma ferramenta Unix/Linux. No Windows, use a alternativa fornecida.

##  Solução: Use `make.bat`

### Comandos Disponíveis

```powershell
# Ver todos os comandos disponíveis
.\make.bat help

# Instalar dependências
.\make.bat install

# Executar testes
.\make.bat test

# Testes com cobertura
.\make.bat test-cov

# Limpar cache
.\make.bat clean

# Executar pipeline
.\make.bat run

# Executar com debug
.\make.bat run-debug

# Verificar .env
.\make.bat check-env

# Validação completa (lint + tests)
.\make.bat validate
```

### Ou use Python diretamente

```powershell
# Testes
python -m pytest tests/ -v

# Testes com cobertura
python -m pytest tests/ -v --cov=src --cov-report=html

# Executar pipeline
python main.py

# Lint
python -m flake8 src tests

# Formatação
python -m black src tests
```

## Alternativas para Instalar Make no Windows

Se preferir usar `make` nativo:

### Opção 1: Chocolatey
```powershell
# Instalar Chocolatey primeiro (https://chocolatey.org/)
choco install make
```

### Opção 2: Git Bash
Use Git Bash que vem com make:
```bash
# No Git Bash
make test
```

### Opção 3: WSL (Windows Subsystem for Linux)
```bash
# No WSL Ubuntu
make test
```

## Comandos PowerShell Equivalentes

| Makefile | Windows (PowerShell) |
|----------|----------------------|
| `make test` | `.\make.bat test` ou `python -m pytest tests/ -v` |
| `make test-cov` | `.\make.bat test-cov` |
| `make clean` | `.\make.bat clean` |
| `make run` | `.\make.bat run` ou `python main.py` |
| `make lint` | `.\make.bat lint` |
| `make format` | `.\make.bat format` |
| `make install` | `.\make.bat install` ou `pip install -r requirements.txt` |

## Limpeza Manual (PowerShell)

Se `make.bat clean` não funcionar:

```powershell
# Remover __pycache__
Get-ChildItem -Path . -Directory -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force

# Remover .pytest_cache
Get-ChildItem -Path . -Directory -Recurse -Filter .pytest_cache | Remove-Item -Recurse -Force

# Remover coverage
Remove-Item -Path .coverage -ErrorAction SilentlyContinue
Remove-Item -Path htmlcov -Recurse -Force -ErrorAction SilentlyContinue

# Remover .pyc
Get-ChildItem -Path . -File -Recurse -Filter *.pyc | Remove-Item -Force
```

## Troubleshooting

### Erro: "Execução de scripts está desabilitada"

```powershell
# Permitir execução de scripts locais
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro: "python não reconhecido"

Adicione Python ao PATH ou use o caminho completo:
```powershell
C:\Python311\python.exe main.py
```

### Erro: "pytest não encontrado"

```powershell
# Instalar pytest
python -m pip install pytest pytest-cov pytest-mock
```

## Quick Start para Windows

```powershell
# 1. Clone o repositório
git clone <url>
cd nome-repo

# 2. Criar ambiente virtual (opcional mas recomendado)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependências
.\make.bat install

# 4. Configurar .env
copy .env.example .env
# Editar .env com suas chaves

# 5. Testar
.\make.bat test

# 6. Executar
.\make.bat run
```

## Executar no Docker (Windows)

Se tiver Docker Desktop instalado:

```powershell
# Build
docker build -t document-pipeline .

# Run
docker run --rm `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/output:/app/output `
  --env-file .env `
  document-pipeline

# Com Docker Compose
docker-compose up
```

**Nota:** No PowerShell, use ` (backtick) para quebra de linha, não `\` (backslash).

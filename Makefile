.PHONY: help install install-dev test test-cov lint format clean run docker-build docker-run

# Configurações
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8

help: ## Mostra esta mensagem de ajuda
	@echo "Document Processing Pipeline - Comandos Disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências de produção
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento
	$(PIP) install -r requirements.txt
	$(PIP) install black isort flake8 pytest pytest-cov pytest-mock

setup: ## Setup completo do ambiente (venv + deps)
	$(PYTHON) -m venv venv
	@echo "Ative o ambiente virtual com: source venv/bin/activate (Linux/Mac) ou venv\Scripts\activate (Windows)"
	@echo "Depois execute: make install"

test: ## Executa testes unitários
	$(PYTEST) tests/ -v

test-cov: ## Executa testes com cobertura
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing --cov-report=html
	@echo "Relatório HTML gerado em htmlcov/index.html"

test-fast: ## Executa apenas testes rápidos (não slow)
	$(PYTEST) tests/ -v -m "not slow"

lint: ## Verifica qualidade do código
	$(FLAKE8) src tests --max-line-length=127 --extend-ignore=E203,W503
	$(BLACK) --check src tests
	$(ISORT) --check-only src tests

format: ## Formata código automaticamente
	$(BLACK) src tests
	$(ISORT) src tests
	@echo "Código formatado com sucesso!"

clean: ## Remove arquivos temporários e cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Limpeza concluída!"

run: ## Executa o pipeline (data/raw → output/)
	$(PYTHON) main.py

run-debug: ## Executa com log detalhado
	$(PYTHON) main.py --log-level DEBUG

run-custom: ## Executa com pasta customizada (make run-custom DIR=meus_docs)
	$(PYTHON) main.py --input-dir $(DIR)

docker-build: ## Constrói imagem Docker
	docker build -t document-pipeline:latest .

docker-run: ## Executa no Docker
	docker run --rm -v $(PWD)/data:/app/data -v $(PWD)/output:/app/output --env-file .env document-pipeline:latest

docker-shell: ## Abre shell no container
	docker run --rm -it -v $(PWD)/data:/app/data --env-file .env document-pipeline:latest /bin/bash

check-env: ## Verifica se .env está configurado
	@if [ ! -f .env ]; then \
		echo "❌ Arquivo .env não encontrado!"; \
		echo "   Copie .env.example para .env e configure suas chaves."; \
		exit 1; \
	fi
	@echo "✅ Arquivo .env encontrado"
	@grep -q "GROQ_API_KEY=gsk-" .env && echo "✅ GROQ_API_KEY configurada" || echo "⚠️  GROQ_API_KEY não configurada"
	@grep -q "OPENAI_API_KEY=sk-" .env && echo "✅ OPENAI_API_KEY configurada" || echo "⚠️  OPENAI_API_KEY não configurada"

validate: lint test ## Validação completa (lint + tests)
	@echo "✅ Validação completa aprovada!"

ci: install-dev validate ## Simula pipeline CI localmente
	@echo "✅ CI pipeline executada com sucesso!"

stats: ## Mostra estatísticas do projeto
	@echo "📊 Estatísticas do Projeto:"
	@echo ""
	@echo "Linhas de código:"
	@find src -name "*.py" | xargs wc -l | tail -1
	@echo ""
	@echo "Linhas de teste:"
	@find tests -name "*.py" | xargs wc -l | tail -1
	@echo ""
	@echo "Arquivos Python:"
	@find src tests -name "*.py" | wc -l
	@echo ""
	@echo "Cobertura de testes:"
	@$(PYTEST) tests/ --cov=src --cov-report=term | grep "TOTAL"

security: ## Verifica vulnerabilidades de segurança
	$(PIP) install safety bandit
	safety check
	bandit -r src

docs: ## Gera documentação (futuro: Sphinx)
	@echo "📚 Documentação disponível em:"
	@echo "  - README.md"
	@echo "  - ARCHITECTURE.md"
	@echo "  - RATE_LIMITING.md"
	@echo "  - REQUISITOS_NAO_FUNCIONAIS.md"

all: clean install-dev validate ## Setup completo + validação
	@echo "🎉 Projeto configurado e validado com sucesso!"

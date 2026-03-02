#!/bin/bash
# Script de instalação automatizada para Linux/Mac

set -e

echo "============================================"
echo " Pipeline de Processamento de Documentos"
echo " Script de Instalação Automatizada"
echo "============================================"
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado!"
    echo "Por favor, instale Python 3.8+"
    exit 1
fi

echo "[OK] Python encontrado: $(python3 --version)"

# Cria ambiente virtual
echo ""
echo "[1/4] Criando ambiente virtual..."
python3 -m venv venv
echo "[OK] Ambiente virtual criado"

# Ativa ambiente virtual
echo ""
echo "[2/4] Ativando ambiente virtual..."
source venv/bin/activate
echo "[OK] Ambiente ativado"

# Instala dependências
echo ""
echo "[3/4] Instalando dependências..."
echo "Isso pode levar alguns minutos..."
pip install --upgrade pip
pip install -r requirements.txt
echo "[OK] Dependências instaladas"

# Cria arquivo .env se não existir
echo ""
echo "[4/4] Configurando ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[AVISO] Arquivo .env criado. EDITE-O com sua OpenAI API key!"
else
    echo "[OK] Arquivo .env já existe"
fi

# Cria diretório de output
mkdir -p output

echo ""
echo "============================================"
echo " INSTALAÇÃO CONCLUÍDA!"
echo "============================================"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo .env com sua OpenAI API key"
echo "2. Coloque seus PDFs na pasta Documentos_Internos/"
echo "3. Execute: python main.py"
echo ""
echo "Para testar um documento:"
echo "  python test_single.py Documentos_Internos/arquivo.pdf"
echo ""

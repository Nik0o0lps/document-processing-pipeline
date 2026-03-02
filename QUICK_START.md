#  Quick Start Guide

## Setup Rápido (5 minutos)

### 1. Instalar Python 3.8+
Verifique se Python está instalado:
```bash
python --version
```

### 2. Criar Ambiente Virtual
```bash
python -m venv venv
```

### 3. Ativar Ambiente Virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar API Key

#### Opção A: Groq Cloud (GRATUITO!)  RECOMENDADO

1. Crie conta em: https://console.groq.com (grátis!)
2. Copie sua API key

```bash
copy .env.example .env
```

Edite `.env`:
```
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-groq-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

#### Opção B: OpenAI (Pago)

```bash
copy .env.example .env
```

Edite `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

 **Veja [GROQ_SETUP.md](GROQ_SETUP.md) para mais detalhes**

### 6. Adicionar Documentos

Coloque seus PDFs na pasta `data/raw/`:

```bash
# Estrutura esperada
data/
└── raw/
    ├── documento1.pdf
    ├── documento2.pdf
    └── ...
```

### 7. Executar o Pipeline

```bash
python main.py
```

Ou para processar de outra pasta:

```bash
python main.py --input-dir "caminho/para/seus/pdfs"
```

## Verificação

Se tudo estiver correto, você verá:
```
2026-03-01 14:30:22 - INFO - Pipeline inicializado
2026-03-01 14:30:22 - INFO - Encontrados 50 arquivos PDF
Processando: 100%|| 50/50 [02:30<00:00,  1.2doc/s]
```

## Testar Um Documento Único

```bash
python test_single.py Documentos_Internos/001_pjpo.pdf
```

## Resultados

Verifique a pasta `output/` para os resultados:
- `resultados_*.json` - Todos os dados extraídos
- `resumo_*.csv` - Resumo do processamento
- `estatisticas_*.txt` - Estatísticas de execução

## Problemas Comuns

### "OPENAI_API_KEY não configurada"
- Certifique-se de ter criado o arquivo `.env`
- Verifique se a API key está correta

### "Nenhum arquivo PDF encontrado"
- Verifique se os PDFs estão em `data/raw/`
- Use `--input-dir` para especificar outro diretório

### Erros de importação
- Certifique-se de ter ativado o ambiente virtual
- Execute `pip install -r requirements.txt` novamente

## Dicas

- Use `--log-level DEBUG` para mais informações
- Ajuste `--max-workers` baseado na capacidade da máquina
- Monitore custos na dashboard da OpenAI


#  Guia de Troubleshooting

## Problemas Comuns e Soluções

### 1. Erro: "OPENAI_API_KEY não configurada"

**Causa:**
- Arquivo `.env` não existe
- API key não está definida corretamente
- Ambiente virtual não carregou o `.env`

**Solução:**
```bash
# 1. Copie o arquivo de exemplo
copy .env.example .env

# 2. Edite o .env e adicione sua key
OPENAI_API_KEY=sk-proj-your-key-here

# 3. Verifique se está correto
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### 2. Erro: "Nenhum arquivo PDF encontrado"

**Causa:**
- Diretório incorreto
- Arquivos não são PDFs
- Permissões de leitura

**Solução:**
```bash
# Verifique se os arquivos existem
dir Documentos_Internos\*.pdf

# Use caminho absoluto se necessário
python main.py --input-dir "C:\caminho\completo\para\pdfs"

# Verifique permissões
icacls Documentos_Internos
```

### 3. Erro: "Import 'pdfplumber' could not be resolved"

**Causa:**
- Dependências não instaladas
- Ambiente virtual não ativado

**Solução:**
```bash
# Ative o ambiente virtual
venv\Scripts\activate

# Reinstale dependências
pip install -r requirements.txt

# Verifique instalação
pip list | findstr pdfplumber
```

### 4. Erro: "Rate limit exceeded" (OpenAI)

**Causa:**
- Muitas requisições simultâneas
- Limite de tokens por minuto excedido

**Solução:**
```bash
# Reduza o número de workers
python main.py --max-workers 1

# Ou adicione delay entre requisições
# Edite llm_client.py e adicione:
import time
time.sleep(1)  # após cada chamada
```

### 5. Erro: "Não foi possível extrair texto do PDF"

**Causa:**
- PDF corrompido
- PDF é apenas imagem sem OCR
- Formato não suportado

**Solução:**
```bash
# Teste o PDF individualmente
python test_single.py Documentos_Internos/arquivo_problema.pdf

# Verifique se o PDF abre normalmente
# Se for imagem, considere OCR adicional:
# pip install pytesseract
```

### 6. Dados extraídos incorretos

**Causa:**
- Qualidade do documento
- Prompt inadequado
- Modelo escolheu campo errado

**Solução:**

**Opção 1: Ajustar temperatura**
```python
# Em llm_client.py, linha da extração
temperature=0  # Mais determinístico
```

**Opção 2: Melhorar prompt**
```python
# Em llm_client.py, melhore as instruções
instrucoes = """
IMPORTANTE: 
- Campo X deve estar no formato Y
- Se não encontrar, deixe vazio
- Valide que...
"""
```

**Opção 3: Usar modelo mais poderoso**
```env
# No .env
OPENAI_MODEL=gpt-4o  # Ao invés de gpt-4o-mini
```

### 7. Processamento muito lento

**Causa:**
- Muitos workers causando contenção
- Rede lenta
- Documentos muito grandes

**Solução:**
```bash
# Reduza workers
python main.py --max-workers 2

# Aumente batch size
python main.py --batch-size 20

# Use logging para identificar gargalo
python main.py --log-level DEBUG --log-file debug.log
```

### 8. Custo muito alto

**Causa:**
- Modelo caro
- Documentos com muito texto
- Muitas tentativas por erro

**Solução:**
```env
# Use modelo mais barato no .env
OPENAI_MODEL=gpt-4o-mini

# Ou truncate texto antes de enviar
# Em document_processor.py, limite caracteres:
texto = texto[:10000]  # Primeiros 10k chars
```

### 9. Erro de memória (MemoryError)

**Causa:**
- Muitos arquivos carregados simultaneamente
- PDFs muito grandes

**Solução:**
```bash
# Reduza batch size
python main.py --batch-size 5

# Reduza workers
python main.py --max-workers 1

# Processe em etapas
# Mova arquivos processados para outra pasta
```

### 10. Caracteres estranhos no output

**Causa:**
- Encoding incorreto
- PDFs com encoding especial

**Solução:**
```python
# Todos os arquivos já usam encoding='utf-8'
# Se persistir, force no PDF reader:

# Em document_processor.py
texto = texto.encode('utf-8', errors='ignore').decode('utf-8')
```

## Debugging Avançado

### 1. Modo Debug Completo

```bash
python main.py --log-level DEBUG --log-file debug.log
```

Isso gera log detalhado com:
- Cada chamada de API
- Texto extraído
- Respostas do LLM
- Stack traces completos

### 2. Testar Componente Individual

**Teste apenas extração de texto:**
```python
from src.document_processor import DocumentProcessor
from src.llm_client import LLMClient

llm = LLMClient()
proc = DocumentProcessor(llm)
texto = proc.extrair_texto_pdf(Path("arquivo.pdf"))
print(texto)
```

**Teste apenas classificação:**
```python
from src.llm_client import LLMClient

llm = LLMClient()
resultado = llm.classificar_documento("texto aqui...")
print(resultado)
```

**Teste apenas extração:**
```python
from src.llm_client import LLMClient

llm = LLMClient()
dados = llm.extrair_informacoes("texto...", "nota_fiscal")
print(dados)
```

### 3. Validar Schemas

```python
from src.schemas import NotaFiscal, ItemNotaFiscal

# Teste se schema aceita seus dados
try:
    nota = NotaFiscal(
        fornecedor="Teste",
        cnpj="12.345.678/0001-90",
        data_emissao="2026-03-01",
        itens=[
            ItemNotaFiscal(
                descricao="Produto",
                quantidade=1,
                valor_total=100.0
            )
        ],
        valor_total=100.0
    )
    print(" Schema válido")
except Exception as e:
    print(f" Erro: {e}")
```

### 4. Monitorar Uso da API

Visite: https://platform.openai.com/usage

Verifique:
- Tokens usados
- Custo acumulado
- Rate limits

### 5. Profile de Performance

```python
# Adicione no início de main.py
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... código normal ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 funções mais lentas
```

## Logs Úteis

### Estrutura dos Logs

```
2026-03-01 14:30:22 - src.pipeline - INFO - Encontrados 50 arquivos PDF
2026-03-01 14:30:23 - src.document_processor - INFO - Processando documento: 001_pjpo.pdf
2026-03-01 14:30:23 - src.document_processor - DEBUG - Texto extraído: 1234 caracteres
2026-03-01 14:30:24 - src.llm_client - INFO - Documento classificado como: nota_fiscal
2026-03-01 14:30:26 - src.llm_client - INFO - Informações extraídas com sucesso
2026-03-01 14:30:26 - src.document_processor - INFO - Documento processado com sucesso em 3.45s
```

### Filtrar Logs Específicos

**Windows:**
```bash
# Apenas erros
python main.py 2>&1 | findstr ERROR

# Apenas um arquivo
python main.py --log-file output.log
type output.log | findstr "001_pjpo"
```

**Linux:**
```bash
# Apenas erros
python main.py 2>&1 | grep ERROR

# Apenas um arquivo
python main.py --log-file output.log
cat output.log | grep "001_pjpo"
```

## Checklist de Diagnóstico

Use este checklist quando tiver problemas:

- [ ] Python 3.8+ instalado? `python --version`
- [ ] Ambiente virtual ativado? Ver `(venv)` no prompt
- [ ] Dependências instaladas? `pip list`
- [ ] Arquivo .env existe? `dir .env`
- [ ] API key válida? Teste no site OpenAI
- [ ] PDFs existem no diretório? `dir Documentos_Internos\*.pdf`
- [ ] Permissões de leitura? `icacls Documentos_Internos`
- [ ] Espaço em disco? `dir`
- [ ] Internet funcionando? `ping platform.openai.com`
- [ ] Firewall não bloqueia? Teste em rede diferente

## Suporte

Se o problema persistir:

1. **Revise logs detalhados**
```bash
python main.py --log-level DEBUG --log-file debug.log
```

2. **Teste com um único documento**
```bash
python test_single.py Documentos_Internos/001_pjpo.pdf
```

3. **Verifique versões**
```bash
python --version
pip list
```

4. **Crie uma issue no GitHub** com:
   - Versão do Python
   - Sistema operacional
   - Comando executado
   - Log completo do erro
   - Arquivo de teste (se possível)

## Performance Benchmarks

### Configuração Recomendada por Escala

| Documentos | max_workers | batch_size | Tempo Estimado | Custo Estimado |
|-----------|-------------|------------|----------------|----------------|
| 50        | 3           | 10         | 3-5 min        | $0.05          |
| 100       | 3           | 10         | 6-10 min       | $0.10          |
| 500       | 5           | 20         | 30-40 min      | $0.50          |
| 1000      | 5           | 20         | 1-1.5 h        | $1.00          |
| 10000     | 10          | 50         | 10-12 h        | $10.00         |

**Nota:** Tempos assumem rede estável e documentos de tamanho médio.


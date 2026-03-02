#  Documentação Técnica

## Arquitetura Detalhada

### Fluxo de Dados Completo

```mermaid
flowchart TD
    Start(["🚀 Início"])
    
    subgraph CLI["🖥️ Interface CLI (main.py)"]
        Args["Parse Argumentos<br/>--directory, --max-workers"]:::cliNode
        Env["Carrega .env<br/>GROQ_API_KEY / OPENAI_API_KEY"]:::cliNode
        Val["Valida Configuração"]:::cliNode
        Args --> Env --> Val
    end
    
    subgraph Pipeline["📦 Pipeline (pipeline.py)"]
        List["🔍 Listar PDFs<br/>glob('*.pdf')"]:::pipelineNode
        Batch["⚡ ThreadPoolExecutor<br/>workers=3"]:::pipelineNode
        Thread1["Thread 1"]:::threadNode
        Thread2["Thread 2"]:::threadNode
        Thread3["Thread 3"]:::threadNode
        List --> Batch
        Batch --> Thread1 & Thread2 & Thread3
    end
    
    subgraph Processor["🔧 Document Processor"]
        Extract["📖 Extração de Texto"]:::processNode
        Try1["1️⃣ pdfplumber"]:::methodNode
        Try2["2️⃣ PyPDF2"]:::methodNode
        Try3["3️⃣ Tesseract OCR"]:::methodNode
        Extract --> Try1
        Try1 -."falha".-> Try2
        Try2 -."falha".-> Try3
    end
    
    subgraph LLM["🧠 LLM Client"]
        Retry["🔄 Retry System<br/>Exponential Backoff<br/>5 tentativas"]:::retryNode
        RateLimit["⏱️ Rate Limiter<br/>30 RPM"]:::rateLimitNode
        Classify["📝 Classificação<br/>tipo + confiança"]:::llmNode
        Extract2["📊 Extração<br/>dados estruturados"]:::llmNode
        
        Retry --> RateLimit
        RateLimit --> Classify
        RateLimit --> Extract2
    end
    
    subgraph Validation["✅ Validação (Pydantic)"]
        Schema1["NotaFiscal"]:::schemaNode
        Schema2["Contrato"]:::schemaNode
        Schema3["RelatorioManutencao"]:::schemaNode
    end
    
    subgraph Storage["💾 Persistência"]
        JSON1["📄 JSON Consolidado<br/>output/json/todos_documentos.json"]:::storageNode
        JSON2["📑 JSON por Tipo<br/>output/json/notas_fiscais.json"]:::storageNode
        CSV1["📊 CSV Resumo<br/>output/csv/resumo.csv"]:::storageNode
        Stats["📈 Estatísticas<br/>output/relatorios/stats.txt"]:::storageNode
    end
    
    Start --> CLI
    CLI --> Pipeline
    Thread1 & Thread2 & Thread3 --> Processor
    Processor --> LLM
    Classify --> Validation
    Extract2 --> Validation
    Validation --> Schema1 & Schema2 & Schema3
    Schema1 & Schema2 & Schema3 --> Storage
    Storage --> JSON1 & JSON2 & CSV1 & Stats
    
    classDef cliNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef pipelineNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef threadNode fill:#fce4ec,stroke:#c2185b,stroke-width:1px,color:#000
    classDef processNode fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef methodNode fill:#fff9c4,stroke:#f9a825,stroke-width:1px,color:#000
    classDef retryNode fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000
    classDef rateLimitNode fill:#e0f2f1,stroke:#00796b,stroke-width:2px,color:#000
    classDef llmNode fill:#fff3e0,stroke:#ff6f00,stroke-width:3px,color:#000
    classDef schemaNode fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#000
    classDef storageNode fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#000
```

### Diagrama de Componentes

```mermaid
graph LR
    subgraph External["🌐 Serviços Externos"]
        Groq["🤖 Groq Cloud<br/>llama-3.3-70b<br/>FREE"]:::groqNode
        OpenAI["🧠 OpenAI<br/>gpt-4o-mini<br/>PAID"]:::openaiNode
    end
    
    subgraph Core["⚙️ Core Application"]
        Main["main.py<br/>CLI Entry"]:::mainNode
        Pipe["pipeline.py<br/>Orchestration"]:::pipeNode
        DocProc["document_processor.py<br/>PDF Processing"]:::docNode
        LLMClient["llm_client.py<br/>AI Integration"]:::llmNode
        Schemas["schemas.py<br/>Data Models"]:::schemaNode
        Config["config.py<br/>Settings"]:::configNode
    end
    
    subgraph Data["📂 Data Layer"]
        Input["data/raw/<br/>Input PDFs"]:::inputNode
        Output["output/<br/>Processed Data"]:::outputNode
    end
    
    Main --> Config
    Main --> Pipe
    Pipe --> DocProc
    DocProc --> LLMClient
    LLMClient --> Groq
    LLMClient --> OpenAI
    LLMClient --> Schemas
    Input --> DocProc
    Schemas --> Output
    
    classDef groqNode fill:#c8e6c9,stroke:#388e3c,stroke-width:3px,color:#000
    classDef openaiNode fill:#bbdefb,stroke:#1976d2,stroke-width:3px,color:#000
    classDef mainNode fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef pipeNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef docNode fill:#e1bee7,stroke:#8e24aa,stroke-width:2px,color:#000
    classDef llmNode fill:#ffccbc,stroke:#e64a19,stroke-width:3px,color:#000
    classDef schemaNode fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#000
    classDef configNode fill:#e0f2f1,stroke:#00796b,stroke-width:2px,color:#000
    classDef inputNode fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000
    classDef outputNode fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#000
```

### Sequência de Processamento (1 Documento)

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 Usuário
    participant M as 📋 main.py
    participant P as ⚙️ Pipeline
    participant D as 🔧 DocProcessor
    participant L as 🧠 LLM Client
    participant G as 🤖 Groq API
    participant V as ✅ Pydantic
    participant S as 💾 Storage
    
    U->>M: python main.py --directory data/raw
    activate M
    M->>M: Parse args + Load .env
    M->>P: processar_documentos()
    activate P
    
    P->>P: Listar PDFs (glob *.pdf)
    P->>P: ThreadPoolExecutor (3 workers)
    
    par Thread 1
        P->>D: processar_documento(doc1.pdf)
        activate D
        
        rect rgb(240, 240, 255)
            Note over D: Extração de Texto
            D->>D: pdfplumber.open()
            alt pdfplumber sucesso
                D->>D: texto extraído ✓
            else pdfplumber falha
                D->>D: PyPDF2.PdfReader()
                alt PyPDF2 sucesso
                    D->>D: texto extraído ✓
                else PyPDF2 falha
                    D->>D: Tesseract OCR
                    D->>D: texto extraído ✓
                end
            end
        end
        
        rect rgb(255, 250, 240)
            Note over D,L: Classificação
            D->>L: classificar_documento(texto)
            activate L
            L->>L: Retry wrapper ativado
            L->>L: Rate limiter check (30 RPM)
            L->>G: POST /chat/completions
            activate G
            G-->>L: {tipo: "nota_fiscal", confiança: 0.95}
            deactivate G
            L-->>D: DocumentoClassificado
            deactivate L
        end
        
        rect rgb(240, 255, 240)
            Note over D,L: Extração
            D->>L: extrair_informacoes(texto, "nota_fiscal")
            activate L
            L->>L: Rate limiter check
            L->>G: POST /chat/completions (structured output)
            activate G
            G-->>L: {fornecedor: "...", cnpj: "...", valor: 1500.00}
            deactivate G
            L-->>D: dados dict
            deactivate L
        end
        
        rect rgb(240, 255, 240)
            Note over D,V: Validação
            D->>V: NotaFiscal.model_validate(dados)
            activate V
            V->>V: Validar tipos + constraints
            V-->>D: NotaFiscal object ✓
            deactivate V
        end
        
        D-->>P: ProcessingResult(status="success")
        deactivate D
    end
    
    P->>P: Aguardar todas threads
    
    rect rgb(230, 245, 255)
        Note over P,S: Persistência
        P->>S: salvar_json(resultados)
        P->>S: salvar_csv(resumo)
        P->>S: gerar_estatisticas()
        S-->>P: Arquivos salvos ✓
    end
    
    P-->>M: Relatório completo
    deactivate P
    M-->>U: ✅ 24/50 processados com sucesso
    deactivate M
```

### Fluxo de Retry e Rate Limiting

```mermaid
stateDiagram-v2
    [*] --> CheckRateLimit: Request LLM
    
    CheckRateLimit --> Wait: RPM excedido
    Wait --> MakeRequest: Aguardou tempo necessário
    CheckRateLimit --> MakeRequest: RPM OK
    
    MakeRequest --> Success: 200 OK
    MakeRequest --> RateLimitError: 429 Rate Limit
    MakeRequest --> OtherError: 5xx Server Error
    
    RateLimitError --> Retry1: Tentativa 1 (wait 1s)
    Retry1 --> MakeRequest
    
    RateLimitError --> Retry2: Tentativa 2 (wait 2s)
    Retry2 --> MakeRequest
    
    RateLimitError --> Retry3: Tentativa 3 (wait 4s)
    Retry3 --> MakeRequest
    
    RateLimitError --> Retry4: Tentativa 4 (wait 8s)
    Retry4 --> MakeRequest
    
    RateLimitError --> Retry5: Tentativa 5 (wait 16s)
    Retry5 --> MakeRequest
    
    RateLimitError --> Failed: 5 tentativas esgotadas
    OtherError --> Failed
    
    Success --> [*]
    Failed --> [*]
    
    note right of CheckRateLimit
        Rate Limiter Preventivo
        Track: requests + timestamps
        Limite: 30 req/min
    end note
    
    note right of RateLimitError
        Exponential Backoff
        Base: 1 segundo
        Multiplicador: 2x
        Max tentativas: 5
    end note
```

### Diagrama de Estados do Documento

```mermaid
stateDiagram-v2
    [*] --> Pending: PDF detectado
    
    Pending --> Extracting: Iniciar processamento
    
    Extracting --> Classifying: Texto extraído
    Extracting --> Failed: Erro extração (3 tentativas)
    
    Classifying --> Extracting_Data: Tipo identificado
    Classifying --> Failed: Erro classificação
    
    Extracting_Data --> Validating: Dados extraídos
    Extracting_Data --> Retry: Rate limit (retry)
    Extracting_Data --> Failed: Erro extração dados
    
    Retry --> Extracting_Data: Após backoff
    
    Validating --> Success: Pydantic OK
    Validating --> Failed: Validação falhou
    
    Success --> [*]: JSON/CSV salvos
    Failed --> [*]: Log de erro
    
    note right of Extracting
        Estratégias:
        1. pdfplumber
        2. PyPDF2
        3. Tesseract OCR
    end note
    
    note right of Extracting_Data
        Retry automático
        com exponential
        backoff
    end note
```    
           - Response format: NotaFiscal | Contrato | ...   
           - Temperature: 0                                  
         Response:                                           
           - Dados estruturados validados por Pydantic      

                  
                  

              SCHEMAS.PY (Validação)                          
                                                              
  Pydantic Models:                                           
    > NotaFiscal                                          
        > fornecedor: str                                
        > cnpj: str                                      
        > itens: List[ItemNotaFiscal]                   
        > valor_total: float                            
                                                             
    > Contrato                                            
        > contratante: str                               
        > contratado: str                                
        > valor_mensal: float                            
                                                             
    > RelatorioManutencao                                 
         > tecnico_responsavel: str                       
         > equipamento: str                               
         > solucao_aplicada: str                          

                  
                  

                         SAÍDA                                
  output/                                                     
   resultados_20240301_143022.json                       
   nota_fiscal_20240301_143022.json                      
   contrato_20240301_143022.json                         
   relatorio_manutencao_20240301_143022.json             
   resumo_20240301_143022.csv                            
   estatisticas_20240301_143022.txt                      

```

## Componentes Principais

### 1. Pipeline (pipeline.py)

**Responsabilidades:**
- Orquestração do fluxo completo
- Gerenciamento de threads paralelas
- Agregação de resultados
- Persistência múltiplos formatos

**Métodos principais:**
- `executar()`: Ponto de entrada principal
- `processar_lote()`: Processa batch com ThreadPoolExecutor
- `salvar_resultados()`: Persiste em JSON, CSV e TXT
- `_gerar_relatorio_estatisticas()`: Gera métricas

**Performance:**
- Max workers: 3 (configurável)
- Batch size: 10 (configurável)
- Progress bar: tqdm

### 2. Document Processor (document_processor.py)

**Responsabilidades:**
- Extração de texto de PDFs
- Coordenação LLM
- Validação de dados
- Tratamento de erros individuais

**Estratégias de extração:**
```python
# Primary: pdfplumber
with pdfplumber.open(pdf) as pdf:
    text = page.extract_text()

# Fallback: PyPDF2
reader = PyPDF2.PdfReader(file)
text = page.extract_text()
```

**Tratamento de erros:**
- Try-catch em cada etapa
- Retorna ProcessingResult com status
- Logging detalhado

### 3. LLM Client (llm_client.py)

**Responsabilidades:**
- Comunicação com OpenAI API
- Structured outputs
- Prompting especializado

**Configuração:**
```python
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"  # Configurável
temperature_classification = 0.1
temperature_extraction = 0
```

**Structured Outputs:**
```python
response = client.beta.chat.completions.parse(
    model=self.model,
    messages=[...],
    response_format=NotaFiscal,  # Pydantic model
    temperature=0
)
```

### 4. Schemas (schemas.py)

**Validação Pydantic:**
- Type hints rigorosos
- Descrições para o LLM
- Validação automática
- Serialização JSON

**Exemplo:**
```python
class NotaFiscal(BaseModel):
    tipo_documento: Literal["nota_fiscal"] = "nota_fiscal"
    fornecedor: str = Field(description="Nome do fornecedor")
    cnpj: str = Field(description="CNPJ do fornecedor")
    itens: List[ItemNotaFiscal]
    valor_total: float
```

## Decisões de Design

### 1. Por que ThreadPoolExecutor?

**Análise:**
-  I/O-bound (PDF reading + API calls)
-  GIL release durante I/O
-  Simples de implementar
-  Controle de concorrência

**Alternativas consideradas:**
-  Multiprocessing: Overhead de serialização
-  AsyncIO: Complexidade adicional
-  Celery: Over-engineering para escopo atual

### 2. Por que múltiplos outputs?

**Justificativa:**
1. **JSON consolidado**: Auditoria completa
2. **JSONs por tipo**: Integração ERP
3. **CSV**: Análise em Excel/BI
4. **TXT stats**: Overview rápido

### 3. Por que two-step (classificação + extração)?

**Vantagens:**
-  Prompts especializados
-  Melhor debugging
-  Flexibilidade (modelos diferentes por etapa)
-  Custo controlado

**Desvantagens:**
-  2x chamadas API (mitigado: classificação usa menos tokens)

### 4. Por que Pydantic?

**Benefícios:**
-  Validação runtime
-  Type safety
-  Integração nativa OpenAI
-  Documentação implícita

## Otimizações

### Custo

1. **Modelo econômico**: gpt-4o-mini
2. **Truncamento**: Limita tokens na classificação
3. **Temperature 0**: Reduz variabilidade
4. **Batch processing**: Amortiza overhead

### Performance

1. **Paralelização**: 3 workers simultâneos
2. **Fallback rápido**: Múltiplas estratégias PDF
3. **Progress tracking**: tqdm para UX

### Robustez

1. **Try-catch granular**: Por documento
2. **Logging detalhado**: Debug facilitado
3. **Validação Pydantic**: Garante integridade
4. **Múltiplos outputs**: Redundância

## Métricas

### Estimativas (50 documentos)

**Custo:**
- Input tokens: ~100k = $0.015
- Output tokens: ~50k = $0.030
- **Total: ~$0.045**

**Tempo:**
- Extração PDF: ~0.5s/doc
- LLM classificação: ~1s/doc
- LLM extração: ~2s/doc
- **Total: ~3.5s/doc média**

**Escalabilidade:**
- 1000 docs: ~58 minutos (~$0.90)
- 10000 docs: ~9.7 horas (~$9.00)
- 100000 docs: ~4 dias (~$90.00)

## Manutenção

### Logs

**Localização:** Console + arquivo opcional

**Níveis:**
- DEBUG: Detalhes de implementação
- INFO: Progresso normal
- WARNING: Problemas não críticos
- ERROR: Falhas que requerem atenção

### Monitoramento

**Métricas chave:**
- Taxa de sucesso (target: >95%)
- Tempo médio (target: <5s)
- Custo por documento (target: <$0.001)

### Troubleshooting

**Problemas comuns:**
1. **Rate limiting**: Reduzir max_workers
2. **PDF corrompido**: Logs identificam arquivo
3. **Extração incorreta**: Ajustar prompts
4. **Custo alto**: Trocar para modelo menor em classificação

## Extensões Futuras

### 1. Suporte a novos tipos de documento

```python
# 1. Adicionar schema em schemas.py
class NotaCreditoDebito(BaseModel):
    ...

# 2. Atualizar DOCUMENT_SCHEMAS
DOCUMENT_SCHEMAS["nota_credito_debito"] = NotaCreditoDebito

# 3. Adicionar instruções em llm_client.py
```

### 2. OCR para imagens

```python
# Integrar pytesseract ou Azure Document Intelligence
from pytesseract import image_to_string
texto = image_to_string(Image.open(image_path))
```

### 3. Fila de processamento

```python
# Integrar com Celery + Redis
@celery.task
def processar_documento_async(caminho):
    ...
```

### 4. API REST

```python
# FastAPI endpoint
@app.post("/processar")
async def processar_upload(file: UploadFile):
    ...
```

## Referências

- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html)


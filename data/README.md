# Estrutura de Dados

## data/raw/

Pasta contendo os documentos PDF não processados para ingestão.

**Tipos de documentos suportados:**
- Notas Fiscais
- Contratos
- Relatórios de Manutenção

**Formato:** PDF (incluindo PDFs escaneados com OCR)

## Uso

### Processar todos os documentos em data/raw/:

```bash
python main.py
```

### Processar de uma pasta específica:

```bash
python main.py --input-dir caminho/para/documentos
```

### Opções adicionais:

```bash
python main.py --help
```

## Estrutura Completa

```
data/
├── raw/              # Documentos originais (input)
│   ├── 001_xxxx.pdf
│   ├── 002_xxxx.pdf
│   └── ...
└── README.md         # Este arquivo
```

Os resultados processados são salvos em `output/` na raiz do projeto.

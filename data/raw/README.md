# Coloque seus documentos PDF aqui

Esta pasta contém os documentos originais (não processados) para o pipeline de processamento.

## Tipos de documentos suportados:

- **Notas Fiscais**: Documentos fiscais com informações de fornecedor, itens e valores
- **Contratos**: Contratos de prestação de serviços
- **Relatórios de Manutenção**: Relatórios técnicos de manutenção de equipamentos

## Formato:

- PDFs (incluindo PDFs escaneados - o sistema tem OCR integrado)

## Executar o processamento:

```bash
# Da raiz do projeto
python main.py
```

Os resultados serão salvos em `output/` na raiz do projeto.

#  Contribuindo para o Projeto

Obrigado por considerar contribuir! Este documento fornece diretrizes para contribuições.

## Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Demonstre empatia com outros membros

## Como Contribuir

### Reportar Bugs

Ao reportar um bug, inclua:

1. **Descrição**: O que você esperava vs. o que aconteceu
2. **Passos para reproduzir**: Lista detalhada
3. **Ambiente**:
   - Versão Python: `python --version`
   - Sistema operacional: Windows/Linux/Mac
   - Versão das dependências: `pip list`
4. **Logs**: Output completo com `--log-level DEBUG`
5. **Arquivo de teste**: Se possível, um PDF que causa o problema

**Template para Issues:**
```markdown
## Descrição
[Descreva o bug]

## Passos para Reproduzir
1. Execute `python main.py`
2. ...

## Comportamento Esperado
[O que deveria acontecer]

## Comportamento Atual
[O que está acontecendo]

## Ambiente
- Python: 3.10.5
- SO: Windows 11
- Versão OpenAI: 1.12.0

## Logs
```
[Cole os logs aqui]
```
```

### Sugerir Melhorias

Para sugerir uma nova funcionalidade:

1. **Verifique issues existentes**: Pode já estar planejada
2. **Descreva o caso de uso**: Por que é útil?
3. **Proposta de implementação**: Como funcionaria?
4. **Alternativas consideradas**: Outras abordagens?

### Pull Requests

#### Antes de Começar

1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie uma branch** para sua feature
   ```bash
   git checkout -b feature/nome-da-feature
   ```

#### Durante o Desenvolvimento

1. **Siga o estilo de código**:
   - PEP 8 para Python
   - Type hints quando possível
   - Docstrings para funções públicas

2. **Escreva código limpo**:
   ```python
   #  BOM
   def processar_documento(arquivo: Path) -> ProcessingResult:
       """
       Processa um documento PDF.
       
       Args:
           arquivo: Caminho para o PDF
           
       Returns:
           Resultado do processamento
       """
       ...
   
   #  RUIM
   def proc(f):
       ...
   ```

3. **Mantenha commits atômicos**:
   ```bash
   #  BOM
   git commit -m "feat: adiciona suporte para OCR em imagens"
   git commit -m "fix: corrige erro ao processar PDFs vazios"
   
   #  RUIM
   git commit -m "várias mudanças"
   ```

4. **Teste suas mudanças**:
   ```bash
   # Teste com um documento
   python test_single.py Documentos_Internos/001_pjpo.pdf
   
   # Teste o pipeline completo
   python main.py
   ```

#### Submetendo o PR

1. **Push para seu fork**:
   ```bash
   git push origin feature/nome-da-feature
   ```

2. **Abra um Pull Request** com:
   - Título claro
   - Descrição do que foi mudado
   - Referência a issues relacionadas (#123)
   - Screenshots se aplicável

3. **Template do PR**:
   ```markdown
   ## Descrição
   [Descreva as mudanças]
   
   ## Motivação e Contexto
   [Por que essa mudança é necessária?]
   
   ## Como Foi Testado?
   - [ ] Teste manual
   - [ ] Pipeline completo
   - [ ] Documento específico
   
   ## Screenshots (se aplicável)
   
   ## Checklist
   - [ ] Código segue o estilo do projeto
   - [ ] Documentação atualizada
   - [ ] Testado localmente
   - [ ] Commit messages seguem convenções
   
   ## Issues Relacionadas
   Closes #123
   ```

## Convenções de Código

### Python

#### Naming

```python
# Classes: PascalCase
class DocumentProcessor:
    pass

# Funções/métodos: snake_case
def processar_documento():
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_WORKERS = 3

# Variáveis: snake_case
nome_arquivo = "doc.pdf"
```

#### Type Hints

```python
#  Use type hints
def extrair_texto(arquivo: Path) -> str:
    ...

def processar_lote(arquivos: List[Path]) -> List[ProcessingResult]:
    ...

# Com Optional
def buscar_config(chave: str) -> Optional[str]:
    ...
```

#### Docstrings

```python
def funcao_exemplo(param1: str, param2: int) -> bool:
    """
    Breve descrição em uma linha.
    
    Descrição mais detalhada se necessário. Pode ter
    múltiplas linhas explicando comportamento complexo.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
        
    Returns:
        Descrição do retorno
        
    Raises:
        ValueError: Quando param2 é negativo
        
    Examples:
        >>> funcao_exemplo("teste", 42)
        True
    """
    ...
```

#### Error Handling

```python
#  Específico e informativo
try:
    resultado = processar_documento(arquivo)
except FileNotFoundError:
    logger.error(f"Arquivo não encontrado: {arquivo}")
    raise
except ValueError as e:
    logger.error(f"Valor inválido ao processar {arquivo}: {e}")
    return erro_result(str(e))

#  Genérico
try:
    ...
except:
    pass
```

### Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: adiciona nova funcionalidade
fix: corrige um bug
docs: mudanças na documentação
style: formatação, ponto e vírgula, etc
refactor: refatoração de código
test: adiciona ou corrige testes
chore: manutenção, dependências, etc
perf: melhoria de performance
```

**Exemplos:**
```bash
feat: adiciona suporte para OCR em imagens
fix: corrige erro ao processar PDFs vazios
docs: atualiza README com novo parâmetro
refactor: simplifica lógica de extração de texto
perf: otimiza processamento paralelo
```

## Áreas para Contribuição

### Iniciante-Friendly

- Melhorar documentação
- Adicionar exemplos
- Corrigir typos
- Adicionar testes unitários
- Melhorar mensagens de erro

### Intermediário

- Adicionar novos tipos de documento
- Implementar cache de resultados
- Melhorar tratamento de erros
- Adicionar validações adicionais
- Otimizar performance

### Avançado

- Implementar OCR para imagens
- Criar API REST com FastAPI
- Adicionar fila de processamento (Celery)
- Implementar web scraping
- Criar dashboard de monitoramento
- Suporte a múltiplos LLM providers

## Testando

### Teste Manual

```bash
# Teste básico
python main.py

# Teste com configuração específica
python main.py --max-workers 2 --log-level DEBUG

# Teste documento único
python test_single.py Documentos_Internos/001_pjpo.pdf
```

### Adicionar Testes Unitários (futuro)

```python
# tests/test_processor.py
import pytest
from src.document_processor import DocumentProcessor

def test_extrair_texto_pdf_valido():
    processor = DocumentProcessor(mock_llm)
    texto = processor.extrair_texto_pdf(Path("test.pdf"))
    assert len(texto) > 0

def test_processar_documento_invalido():
    processor = DocumentProcessor(mock_llm)
    with pytest.raises(ValueError):
        processor.processar_documento(Path("invalido.pdf"))
```

## Recursos

- [Documentação OpenAI](https://platform.openai.com/docs)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Python Threading](https://docs.python.org/3/library/threading.html)
- [PEP 8 Style Guide](https://pep8.org/)

## Comunidade

- Seja paciente com revisões
- Esteja aberto a feedback
- Ajude outros contribuidores
- Comemore sucessos!

## Contato

Para dúvidas sobre contribuições:
- Abra uma **Discussion** no GitHub
- Ou crie uma **Issue** com a tag `question`

---

**Obrigado por contribuir! **


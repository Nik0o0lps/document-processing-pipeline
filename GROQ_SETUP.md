#  Como Usar com Groq Cloud (GRATUITO!)

O **Groq Cloud** oferece API **100% GRATUITA** e é **extremamente rápido** (até 10x mais rápido que OpenAI)!

## Por que Groq?

-  **GRATUITO**: Sem custos
-  **RÁPIDO**: Inferência em hardware especializado (LPU)
-  **FÁCIL**: API compatível com OpenAI
-  **ÓTIMOS MODELOS**: Llama 3.3 70B, Mixtral, etc.

## Setup Rápido (5 minutos)

### 1. Criar Conta no Groq

1. Acesse: https://console.groq.com
2. Crie uma conta (grátis)
3. Vá em **API Keys**
4. Clique em **Create API Key**
5. Copie sua chave (formato: `gsk_...`)

### 2. Configurar o Projeto

```bash
# 1. Copie o arquivo de exemplo
copy .env.example .env

# 2. Edite o .env
notepad .env
```

No arquivo `.env`, configure:
```env
# Use Groq (gratuito!)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_sua_chave_aqui

# Modelos disponíveis no Groq (todos gratuitos):
# - llama-3.3-70b-versatile (RECOMENDADO - melhor qualidade)
# - llama-3.1-70b-versatile
# - mixtral-8x7b-32768
# - gemma2-9b-it
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Instalar Dependências

```bash
# Ative o ambiente virtual
venv\Scripts\activate

# Instale ou atualize
pip install -r requirements.txt
```

### 4. Executar!

```bash
python main.py
```

## Modelos Groq Disponíveis

| Modelo | Tokens/min | Qualidade | Recomendado Para |
|--------|------------|-----------|------------------|
| **llama-3.3-70b-versatile** | 30K |  | **Uso geral** (RECOMENDADO) |
| llama-3.1-70b-versatile | 20K |  | Alternativa ao 3.3 |
| mixtral-8x7b-32768 | 5K |  | Contexto grande |
| gemma2-9b-it | 15K |  | Mais rápido |

**Recomendação**: Use `llama-3.3-70b-versatile` - melhor qualidade!

## Comparação: Groq vs OpenAI

| Característica | Groq | OpenAI |
|----------------|------|--------|
| **Custo** |  **GRATUITO** |  Pago ($) |
| **Velocidade** |  **Muito rápido** | Normal |
| **Qualidade** |  (Llama 3.3 70B) |  (GPT-4) |
| **Limites** | Rate limits generosos | Baseado em créditos |
| **Setup** | Simples | Simples |

## Trocar entre Groq e OpenAI

É fácil trocar de provedor! Basta editar o `.env`:

### Usar Groq (gratuito):
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_sua_chave_aqui
GROQ_MODEL=llama-3.3-70b-versatile
```

### Usar OpenAI (pago):
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
```

## Configuração Avançada

### Ajustar Qualidade vs Velocidade

Para **mais qualidade** (mais lento):
```env
GROQ_MODEL=llama-3.3-70b-versatile
```

Para **mais velocidade** (menor qualidade):
```env
GROQ_MODEL=gemma2-9b-it
```

### Testar Diferentes Modelos

```bash
# Teste com Llama 3.3 70B
python main.py

# Edite .env para outro modelo e teste novamente
```

## Troubleshooting

### "GROQ_API_KEY não configurada"

**Solução:**
1. Verifique se criou o arquivo `.env`
2. Certifique-se de ter copiado a chave corretamente
3. A chave deve começar com `gsk_`

### "Rate limit exceeded"

**Causa**: Muitas requisições simultâneas

**Solução**:
```bash
# Reduza workers
python main.py --max-workers 1
```

### Erro de JSON parsing

**Causa**: Groq às vezes retorna JSON mal formatado

**Solução**: O código já trata isso! Se persistir:
1. Tente outro modelo (llama-3.3-70b é mais estável)
2. Verifique logs: `python main.py --log-level DEBUG`

## Dicas

1. **Primeira vez?** Use Groq! É grátis e funciona muito bem
2. **Precisa da melhor qualidade?** OpenAI GPT-4 é superior, mas custa
3. **Processando muitos documentos?** Groq é ideal (grátis + rápido)
4. **Ambiente de produção?** Considere OpenAI para maior confiabilidade

## Performance Estimada (50 documentos)

### Com Groq (GRATUITO):
- Tempo: **2-4 minutos**
- Custo: **$0.00** (GRÁTIS!)
- Velocidade: Muito rápido

### Com OpenAI gpt-4o-mini:
- Tempo: **3-5 minutos**
- Custo: **~$0.045**
- Velocidade: Normal

### Com OpenAI gpt-4o:
- Tempo: **4-6 minutos**
- Custo: **~$0.20**
- Velocidade: Normal
- Qualidade: Máxima

## Links Úteis

- **Groq Console**: https://console.groq.com
- **Groq Docs**: https://console.groq.com/docs
- **Modelos disponíveis**: https://console.groq.com/docs/models
- **Rate limits**: https://console.groq.com/docs/rate-limits

## FAQ

**Q: Groq é realmente gratuito?**  
A: Sim! 100% gratuito com limites generosos.

**Q: Qual a qualidade comparado ao GPT-4?**  
A: Llama 3.3 70B é excelente! Para a maioria dos casos é suficiente.

**Q: Posso usar os dois (Groq e OpenAI)?**  
A: Sim! Configure ambas as keys no `.env` e troque o `LLM_PROVIDER`.

**Q: Tem limite de documentos?**  
A: Groq tem rate limits, mas são generosos. Para 50 docs não terá problema.

**Q: É seguro?**  
A: Sim! Groq é uma empresa legítima com infraestrutura enterprise.

---

## Comece Agora!

```bash
# 1. Obtenha sua chave gratuita
# Acesse: https://console.groq.com

# 2. Configure
copy .env.example .env
notepad .env

# 3. Execute!
python main.py
```

**Resultado**: Pipeline funcionando 100% GRÁTIS! 


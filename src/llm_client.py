"""
Cliente LLM para classificação e extração de informações de documentos.
Usa a API da OpenAI com structured outputs para garantir formato consistente.
Inclui retry automático com exponential backoff para rate limits.
"""

import json
import logging
import os
import time
from functools import wraps
from typing import Any, Callable, Dict, Literal, Optional

from pydantic import BaseModel

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from groq import Groq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from .schemas import DOCUMENT_SCHEMAS, DocumentoClassificado

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0,
):
    """Decorator que implementa retry com exponential backoff para rate limits.

    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        exponential_base: Base para crescimento exponencial
        max_delay: Delay máximo em segundos
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e
                    error_message = str(e).lower()

                    # Identifica erros de rate limit
                    is_rate_limit = any(
                        [
                            "rate_limit" in error_message,
                            "rate limit" in error_message,
                            "too many requests" in error_message,
                            "429" in error_message,
                            "quota" in error_message,
                        ]
                    )

                    # Apenas faz retry para rate limits
                    if not is_rate_limit:
                        logger.error(f"Erro não relacionado a rate limit: {e}")
                        raise

                    if attempt < max_retries:
                        # Calcula delay com exponential backoff
                        current_delay = min(
                            delay * (exponential_base**attempt), max_delay
                        )
                        logger.warning(
                            f"Rate limit atingido. Tentativa {attempt + 1}/{max_retries}. "
                            f"Aguardando {current_delay:.1f}s antes de tentar novamente..."
                        )
                        time.sleep(current_delay)
                    else:
                        logger.error(
                            f"Rate limit persistente após {max_retries} tentativas. "
                            f"Último erro: {e}"
                        )
                        raise

            # Se chegou aqui, esgotou as tentativas
            raise last_exception

        return wrapper

    return decorator


class LLMClient:
    """Cliente para interação com LLM (OpenAI ou Groq).

    Features:
    - Retry automático com exponential backoff para rate limits
    - Rate limiting preventivo (controle de QPM)
    - Logging detalhado de erros e tentativas
    """

    def __init__(
        self,
        provider: Optional[Literal["openai", "groq"]] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 5,
        enable_rate_limiter: bool = True,
        requests_per_minute: int = 30,
    ):
        """
        Inicializa o cliente LLM.

        Args:
            provider: Provedor LLM ("openai" ou "groq"). Se None, usa variável de ambiente.
            api_key: API key (se None, usa variável de ambiente)
            model: Modelo a ser usado (se None, usa variável de ambiente)
            max_retries: Número máximo de tentativas em caso de rate limit
            enable_rate_limiter: Se True, controla velocidade de requisições preventivamente
            requests_per_minute: Limite de requisições por minuto (rate limiter preventivo)
        """
        self.max_retries = max_retries
        self.enable_rate_limiter = enable_rate_limiter
        self.requests_per_minute = requests_per_minute

        # Controle de rate limiting preventivo
        self._request_times = []
        self._rate_limit_window = 60.0  # 1 minuto em segundos
        # Determina o provedor
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq").lower()

        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI não instalado. Execute: pip install openai")

            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY não configurada")

            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.client = OpenAI(api_key=self.api_key)
            self.supports_structured_output = True

        elif self.provider == "groq":
            if not GROQ_AVAILABLE:
                raise ImportError("Groq não instalado. Execute: pip install groq")

            self.api_key = api_key or os.getenv("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "GROQ_API_KEY não configurada. Obtenha em: https://console.groq.com"
                )

            self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            self.client = Groq(api_key=self.api_key)
            # Groq também suporta structured outputs via response_format
            self.supports_structured_output = True

        else:
            raise ValueError(
                f"Provedor desconhecido: {self.provider}. Use 'openai' ou 'groq'"
            )

        logger.info(
            f"LLM Client inicializado: provider={self.provider}, model={self.model}, "
            f"max_retries={self.max_retries}, rate_limiter={'enabled' if self.enable_rate_limiter else 'disabled'}"
        )

    def _wait_if_rate_limited(self):
        """Rate limiter preventivo: aguarda se estiver próximo do limite."""
        if not self.enable_rate_limiter:
            return

        current_time = time.time()

        # Remove requisições antigas (fora da janela de 1 minuto)
        self._request_times = [
            t for t in self._request_times if current_time - t < self._rate_limit_window
        ]

        # Se atingiu o limite, aguarda
        if len(self._request_times) >= self.requests_per_minute:
            # Calcula quanto tempo deve esperar
            oldest_request = self._request_times[0]
            wait_time = self._rate_limit_window - (current_time - oldest_request)

            if wait_time > 0:
                logger.info(
                    f"Rate limiter preventivo: aguardando {wait_time:.1f}s "
                    f"({len(self._request_times)}/{self.requests_per_minute} requisições no último minuto)"
                )
                time.sleep(wait_time)
                # Atualiza tempo após aguardar
                current_time = time.time()

        # Registra esta requisição
        self._request_times.append(current_time)

    @retry_with_exponential_backoff(max_retries=5, initial_delay=1.0)
    def classificar_documento(self, texto: str) -> DocumentoClassificado:
        """
        Classifica um documento em um dos tipos conhecidos.

        Args:
            texto: Texto extraído do documento

        Returns:
            DocumentoClassificado com tipo e confiança
        """
        prompt = f"""Analise o seguinte texto extraído de um documento e classifique-o em um dos seguintes tipos:

1. nota_fiscal - Documento fiscal com lista de itens, valores e informações do fornecedor
2. contrato - Contrato de prestação de serviços com partes, objeto e vigência
3. relatorio_manutencao - Relatório técnico de manutenção de equipamentos

Texto do documento:
{texto[:3000]}  # Limita para evitar tokens excessivos

Retorne apenas o tipo de documento identificado em formato JSON."""

        # Rate limiter preventivo
        self._wait_if_rate_limited()

        try:
            if self.provider == "openai":
                response = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em classificação de documentos empresariais. Analise cuidadosamente o texto e identifique o tipo correto.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format=DocumentoClassificado,
                    temperature=0.1,
                )
                resultado = response.choices[0].message.parsed

            elif self.provider == "groq":
                # Groq usa response_format com json_schema
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em classificação de documentos empresariais. Analise cuidadosamente o texto e identifique o tipo correto. Retorne sempre em formato JSON.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )
                # Parse manualmente o JSON
                content = response.choices[0].message.content
                data = json.loads(content)

                # Normalizar campo tipo_documento -> tipo
                if "tipo_documento" in data and "tipo" not in data:
                    data["tipo"] = data.pop("tipo_documento")

                resultado = DocumentoClassificado(**data)

            logger.info(f"Documento classificado como: {resultado.tipo}")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao classificar documento: {e}")
            raise

    @retry_with_exponential_backoff(max_retries=5, initial_delay=1.0)
    def extrair_informacoes(self, texto: str, tipo_documento: str) -> Dict[str, Any]:
        """
        Extrai informações estruturadas de um documento baseado em seu tipo.

        Args:
            texto: Texto extraído do documento
            tipo_documento: Tipo do documento (nota_fiscal, contrato, relatorio_manutencao)

        Returns:
            Dicionário com informações extraídas no formato do schema
        """
        if tipo_documento not in DOCUMENT_SCHEMAS:
            raise ValueError(f"Tipo de documento desconhecido: {tipo_documento}")

        schema_class = DOCUMENT_SCHEMAS[tipo_documento]

        # Instruções específicas por tipo de documento
        instrucoes = {
            "nota_fiscal": """Extraia as seguintes informações da nota fiscal:
- Nome do fornecedor
- CNPJ (formato: XX.XXX.XXX/XXXX-XX)
- Data de emissão (formato: YYYY-MM-DD)
- Número da nota fiscal (se disponível)
- Lista completa de itens com descrição, quantidade, valor unitário e valor total
- Valor total da nota fiscal

IMPORTANTE: Para itens, sempre extraia todos os campos. Se o valor unitário não estiver explícito, calcule dividindo o valor total pela quantidade.""",
            "contrato": """Extraia as seguintes informações do contrato:
- Nome do contratante (quem está contratando)
- Nome do contratado (quem está sendo contratado)
- Objeto do contrato (descrição do que está sendo contratado)
- Data de início da vigência (formato: YYYY-MM-DD)
- Data de fim da vigência (formato: YYYY-MM-DD)
- Valor mensal do contrato
- Número do contrato (se disponível)""",
            "relatorio_manutencao": """Extraia as seguintes informações do relatório:
- Data da manutenção (formato: YYYY-MM-DD)
- Nome do técnico responsável
- Nome/identificação do equipamento
- Descrição completa do problema encontrado
- Descrição completa da solução aplicada
- Número da ordem de serviço (se disponível)""",
        }

        prompt = f"""{instrucoes[tipo_documento]}

Texto do documento:
{texto}

Extraia todas as informações solicitadas de forma precisa. Use o formato de data YYYY-MM-DD.
Para valores monetários, use apenas números (sem símbolos de moeda)."""

        # Rate limiter preventivo
        self._wait_if_rate_limited()

        try:
            if self.provider == "openai":
                response = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em extração de dados de documentos. Extraia as informações de forma precisa e estruturada.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format=schema_class,
                    temperature=0,
                )
                resultado = response.choices[0].message.parsed

            elif self.provider == "groq":
                # Groq: adiciona schema no prompt e usa json_object
                prompt_com_schema = f"""{prompt}

Retorne os dados no seguinte formato JSON (siga EXATAMENTE esta estrutura):
{json.dumps(schema_class.model_json_schema(), indent=2)}"""

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um especialista em extração de dados de documentos. Extraia as informações de forma precisa e estruturada. Retorne APENAS JSON válido.",
                        },
                        {"role": "user", "content": prompt_com_schema},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0,
                )
                # Parse e valida
                content = response.choices[0].message.content
                data = json.loads(content)
                resultado = schema_class(**data)

            logger.info(
                f"Informações extraídas com sucesso para tipo: {tipo_documento}"
            )

            # Converte para dict
            return resultado.model_dump()

        except Exception as e:
            logger.error(f"Erro ao extrair informações: {e}")
            raise

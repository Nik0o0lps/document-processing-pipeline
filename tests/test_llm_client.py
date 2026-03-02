"""Testes para o LLM Client com mocks."""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.llm_client import LLMClient, retry_with_exponential_backoff
from src.schemas import DocumentoClassificado


class TestRetryDecorator:
    """Testes para o decorator de retry."""

    def test_retry_sucesso_primeira_tentativa(self):
        """Testa função que funciona na primeira tentativa."""
        mock_func = Mock(return_value="success")
        decorated = retry_with_exponential_backoff(max_retries=3)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_rate_limit(self):
        """Testa retry em caso de rate limit."""
        mock_func = Mock(
            side_effect=[
                Exception("Rate limit exceeded"),
                Exception("Rate limit exceeded"),
                "success",
            ]
        )
        decorated = retry_with_exponential_backoff(
            max_retries=3, initial_delay=0.01  # Delay pequeno para testes rápidos
        )(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_nao_rate_limit(self):
        """Testa que não faz retry para erros não relacionados a rate limit."""
        mock_func = Mock(side_effect=ValueError("Invalid input"))
        decorated = retry_with_exponential_backoff(max_retries=3)(mock_func)

        with pytest.raises(ValueError):
            decorated()

        # Deve falhar imediatamente, sem retries
        assert mock_func.call_count == 1

    def test_retry_esgota_tentativas(self):
        """Testa quando esgota todas as tentativas."""
        mock_func = Mock(side_effect=Exception("Rate limit exceeded"))
        decorated = retry_with_exponential_backoff(max_retries=2, initial_delay=0.01)(
            mock_func
        )

        with pytest.raises(Exception):
            decorated()

        # 1 tentativa original + 2 retries = 3 chamadas
        assert mock_func.call_count == 3


class TestLLMClientInit:
    """Testes para inicialização do LLMClient."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("src.llm_client.Groq")
    def test_init_groq(self, mock_groq_class):
        """Testa inicialização com Groq."""
        client = LLMClient(provider="groq")

        assert client.provider == "groq"
        assert client.model == "llama-3.3-70b-versatile"
        assert client.max_retries == 5
        assert client.enable_rate_limiter is True
        mock_groq_class.assert_called_once()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("src.llm_client.OpenAI")
    def test_init_openai(self, mock_openai_class):
        """Testa inicialização com OpenAI."""
        client = LLMClient(provider="openai")

        assert client.provider == "openai"
        assert client.model == "gpt-4o-mini"
        mock_openai_class.assert_called_once()

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("src.llm_client.Groq")
    def test_init_custom_params(self, mock_groq_class):
        """Testa inicialização com parâmetros customizados."""
        client = LLMClient(
            provider="groq",
            max_retries=10,
            enable_rate_limiter=False,
            requests_per_minute=100,
        )

        assert client.max_retries == 10
        assert client.enable_rate_limiter is False
        assert client.requests_per_minute == 100

    def test_init_sem_api_key(self):
        """Testa erro quando API key não está configurada."""
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            LLMClient(provider="groq")


class TestRateLimiter:
    """Testes para o rate limiter preventivo."""

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("src.llm_client.Groq")
    @patch("time.sleep")
    def test_rate_limiter_aguarda(self, mock_sleep, mock_groq):
        """Testa que rate limiter aguarda quando atinge limite."""
        client = LLMClient(
            provider="groq", enable_rate_limiter=True, requests_per_minute=2
        )

        # Simula 3 requisições (3ª deve aguardar)
        client._wait_if_rate_limited()  # 1ª
        client._wait_if_rate_limited()  # 2ª
        client._wait_if_rate_limited()  # 3ª - deve aguardar

        # Deve ter chamado sleep pelo menos uma vez
        assert mock_sleep.call_count >= 1

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    @patch("src.llm_client.Groq")
    def test_rate_limiter_desabilitado(self, mock_groq):
        """Testa que rate limiter desabilitado não aguarda."""
        client = LLMClient(provider="groq", enable_rate_limiter=False)

        # Múltiplas chamadas não devem aguardar
        for _ in range(100):
            client._wait_if_rate_limited()

        # Não deve ter requisições registradas
        assert len(client._request_times) == 0


@pytest.fixture
def mock_groq_client():
    """Fixture que cria um client Groq mockado."""
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
        with patch("src.llm_client.Groq") as mock_groq_class:
            mock_client = Mock()
            mock_groq_class.return_value = mock_client

            client = LLMClient(
                provider="groq",
                enable_rate_limiter=False,  # Desabilita para testes rápidos
                max_retries=0,  # Sem retries para testes simples
            )
            client.client = mock_client

            yield client, mock_client


class TestClassificacao:
    """Testes para classificação de documentos."""

    def test_classificacao_groq_success(self, mock_groq_client):
        """Testa classificação bem-sucedida com Groq."""
        client, mock_api = mock_groq_client

        # Mock da resposta da API
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            '{"tipo": "nota_fiscal", "confianca": 0.95}'
        )
        mock_api.chat.completions.create.return_value = mock_response

        resultado = client.classificar_documento("Texto de teste")

        assert isinstance(resultado, DocumentoClassificado)
        assert resultado.tipo == "nota_fiscal"
        assert resultado.confianca == 0.95


class TestExtracao:
    """Testes para extração de informações."""

    def test_extracao_tipo_invalido(self, mock_groq_client):
        """Testa erro com tipo de documento inválido."""
        client, _ = mock_groq_client

        with pytest.raises(ValueError, match="Tipo de documento desconhecido"):
            client.extrair_informacoes("texto", "tipo_invalido")

    def test_extracao_nota_fiscal_success(self, mock_groq_client):
        """Testa extração de nota fiscal."""
        client, mock_api = mock_groq_client

        # Mock da resposta
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "fornecedor": "Empresa LTDA",
            "cnpj": "12.345.678/0001-90",
            "data_emissao": "2026-03-01",
            "numero_nota": "12345",
            "itens": [],
            "valor_total": 100.0
        }"""
        mock_api.chat.completions.create.return_value = mock_response

        resultado = client.extrair_informacoes("texto nota fiscal", "nota_fiscal")

        assert resultado["fornecedor"] == "Empresa LTDA"
        assert resultado["valor_total"] == 100.0


class TestIntegracaoLLM:
    """Testes de integração (podem ser marcados como slow)."""

    @pytest.mark.skip(reason="Requer API key válida e créditos")
    def test_real_api_call(self):
        """Teste real com API (skip por padrão)."""
        # Este teste só deve rodar manualmente com --runreal flag
        pass

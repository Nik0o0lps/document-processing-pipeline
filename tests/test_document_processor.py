"""Testes para o Document Processor."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.document_processor import DocumentProcessor, ProcessingResult
from src.llm_client import LLMClient
from src.schemas import DocumentoClassificado


@pytest.fixture
def mock_llm_client():
    """Fixture que cria um LLM client mockado."""
    client = Mock(spec=LLMClient)
    return client


@pytest.fixture
def temp_pdf_dir():
    """Fixture que cria um diretório temporário com PDF fake."""
    temp_dir = Path(tempfile.mkdtemp())

    # Cria um arquivo PDF fake (só para testes de erro)
    fake_pdf = temp_dir / "test.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%fake content")

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


class TestDocumentProcessor:
    """Testes para DocumentProcessor."""

    def test_init(self, mock_llm_client):
        """Testa inicialização do processor."""
        processor = DocumentProcessor(mock_llm_client)

        assert processor.llm_client == mock_llm_client

    @patch("pdfplumber.open")
    def test_extrair_texto_pdfplumber_success(self, mock_pdfplumber, mock_llm_client):
        """Testa extração de texto bem-sucedida com pdfplumber."""
        processor = DocumentProcessor(mock_llm_client)

        # Mock do PDF
        mock_pdf = MagicMock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Texto extraído do PDF"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

        texto = processor.extrair_texto_pdf("fake.pdf")

        assert "Texto extraído do PDF" in texto

    @patch("pdfplumber.open", side_effect=Exception("pdfplumber failed"))
    @patch("PyPDF2.PdfReader")
    def test_extrair_texto_fallback_pypdf2(
        self, mock_pypdf2, mock_pdfplumber, mock_llm_client
    ):
        """Testa fallback para PyPDF2 quando pdfplumber falha."""
        processor = DocumentProcessor(mock_llm_client)

        # Mock do PyPDF2
        mock_reader = Mock()
        mock_page = Mock()
        mock_page.extract_text.return_value = "Texto do PyPDF2\n"
        mock_reader.pages = [mock_page]
        mock_pypdf2.return_value = mock_reader

        from unittest.mock import mock_open

        with patch("builtins.open", mock_open(read_data=b"fake pdf")):
            texto = processor.extrair_texto_pdf("fake.pdf")

        assert "Texto do PyPDF2" in texto

    def test_extrair_texto_pdf_vazio(self, mock_llm_client):
        """Testa erro quando PDF não contém texto."""
        processor = DocumentProcessor(mock_llm_client)

        with patch("pdfplumber.open") as mock_pdfplumber, patch(
            "PyPDF2.PdfReader"
        ) as mock_pypdf2, patch("builtins.open", Mock()):

            # Mock pdfplumber retornando vazio
            mock_pdf = MagicMock()
            mock_page = Mock()
            mock_page.extract_text.return_value = ""
            mock_pdf.pages = [mock_page]
            mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

            # Mock PyPDF2 também retornando vazio
            mock_reader = Mock()
            mock_page_pypdf = Mock()
            mock_page_pypdf.extract_text.return_value = ""
            mock_reader.pages = [mock_page_pypdf]
            mock_pypdf2.return_value = mock_reader

            with pytest.raises(ValueError, match="Não foi possível extrair texto"):
                processor.extrair_texto_pdf("fake.pdf")


class TestProcessingResult:
    """Testes para ProcessingResult."""

    def test_resultado_sucesso(self):
        """Testa criação de resultado de sucesso."""
        resultado = ProcessingResult(
            arquivo="test.pdf",
            status="success",
            tipo_documento="nota_fiscal",
            dados_extraidos={"fornecedor": "Empresa"},
            tempo_processamento=2.5,
        )

        assert resultado.status == "success"
        assert resultado.tipo_documento == "nota_fiscal"
        assert resultado.tempo_processamento == 2.5

    def test_resultado_erro(self):
        """Testa criação de resultado de erro."""
        resultado = ProcessingResult(
            arquivo="test.pdf",
            status="error",
            erro="Rate limit exceeded",
            tempo_processamento=0.5,
        )

        assert resultado.status == "error"
        assert resultado.erro == "Rate limit exceeded"
        assert resultado.tipo_documento is None


class TestProcessarDocumento:
    """Testes para processamento completo de documento."""

    @patch("src.document_processor.DocumentProcessor.extrair_texto_pdf")
    def test_processar_documento_sucesso(self, mock_extrair, mock_llm_client):
        """Testa processamento bem-sucedido de documento."""
        processor = DocumentProcessor(mock_llm_client)

        # Mock extração de texto
        mock_extrair.return_value = "Texto do documento"

        # Mock classificação
        mock_llm_client.classificar_documento.return_value = DocumentoClassificado(
            tipo="nota_fiscal", confianca=0.95
        )

        # Mock extração
        mock_llm_client.extrair_informacoes.return_value = {
            "fornecedor": "Empresa LTDA",
            "valor_total": 100.0,
        }

        resultado = processor.processar_documento("test.pdf")

        assert resultado.status == "success"
        assert resultado.tipo_documento == "nota_fiscal"
        assert resultado.dados["fornecedor"] == "Empresa LTDA"
        assert resultado.tempo_processamento >= 0

    @patch("src.document_processor.DocumentProcessor.extrair_texto_pdf")
    def test_processar_documento_erro_extracao(self, mock_extrair, mock_llm_client):
        """Testa tratamento de erro na extração de texto."""
        processor = DocumentProcessor(mock_llm_client)

        mock_extrair.side_effect = Exception("Erro ao ler PDF")

        resultado = processor.processar_documento("test.pdf")

        assert resultado.status == "error"
        assert "Erro ao ler PDF" in resultado.erro

    @patch("src.document_processor.DocumentProcessor.extrair_texto_pdf")
    def test_processar_documento_erro_classificacao(
        self, mock_extrair, mock_llm_client
    ):
        """Testa tratamento de erro na classificação."""
        processor = DocumentProcessor(mock_llm_client)

        mock_extrair.return_value = "Texto"
        mock_llm_client.classificar_documento.side_effect = Exception("Rate limit")

        resultado = processor.processar_documento("test.pdf")

        assert resultado.status == "error"
        assert "Rate limit" in resultado.erro

    @patch("src.document_processor.DocumentProcessor.extrair_texto_pdf")
    def test_processar_documento_erro_extracao_dados(
        self, mock_extrair, mock_llm_client
    ):
        """Testa tratamento de erro na extração de dados."""
        processor = DocumentProcessor(mock_llm_client)

        mock_extrair.return_value = "Texto"
        mock_llm_client.classificar_documento.return_value = DocumentoClassificado(
            tipo="nota_fiscal"
        )
        mock_llm_client.extrair_informacoes.side_effect = Exception("API error")

        resultado = processor.processar_documento("test.pdf")

        assert resultado.status == "error"
        assert "API error" in resultado.erro


class TestIntegracaoProcessor:
    """Testes de integração do processor."""

    def test_processor_file_not_found(self, mock_llm_client):
        """Testa erro quando arquivo não existe."""
        processor = DocumentProcessor(mock_llm_client)

        resultado = processor.processar_documento("arquivo_inexistente.pdf")

        assert resultado.status == "error"
        assert resultado.erro is not None
        assert len(resultado.erro) > 0

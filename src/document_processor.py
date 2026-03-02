"""
Processador de documentos PDF.
Extrai texto e coordena classificação e extração de dados.
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pdfplumber
import PyPDF2

try:
    import os

    import pytesseract
    from pdf2image import convert_from_path

    OCR_AVAILABLE = True

    # Configuração do Tesseract OCR
    # Configure via TESSERACT_CMD no .env ou use o path padrão do Windows
    tesseract_cmd = os.getenv(
        "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    if os.path.exists(tesseract_cmd):
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # Configuração do Poppler
    # Configure via POPPLER_PATH no .env ou use o path padrão
    POPPLER_PATH = os.getenv("POPPLER_PATH")
    if POPPLER_PATH and not os.path.exists(POPPLER_PATH):
        POPPLER_PATH = None  # Tenta usar PATH do sistema

    logger_temp = logging.getLogger(__name__)
    logger_temp.info("OCR configurado: Tesseract + Poppler")
except ImportError:
    OCR_AVAILABLE = False
    POPPLER_PATH = None

from .llm_client import LLMClient
from .schemas import ProcessingResult

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processador de documentos PDF com extração de texto e dados estruturados."""

    def __init__(self, llm_client: LLMClient):
        """
        Inicializa o processador de documentos.

        Args:
            llm_client: Cliente LLM para classificação e extração
        """
        self.llm_client = llm_client
        logger.info("Document Processor inicializado")

    def extrair_texto_pdf(self, caminho_pdf: Path) -> str:
        """
        Extrai texto de um arquivo PDF usando múltiplas estratégias.

        Args:
            caminho_pdf: Caminho para o arquivo PDF

        Returns:
            Texto extraído do PDF
        """
        texto = ""

        # Estratégia 1: pdfplumber (melhor para documentos scaneados com OCR)
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n"

                if texto.strip():
                    logger.debug(
                        f"Texto extraído com pdfplumber: {len(texto)} caracteres"
                    )
                    return texto
        except Exception as e:
            logger.warning(f"Erro ao extrair com pdfplumber: {e}")

        # Estratégia 2: PyPDF2 (fallback)
        try:
            with open(caminho_pdf, "rb") as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                for pagina in leitor.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n"

                if texto.strip():
                    logger.debug(f"Texto extraído com PyPDF2: {len(texto)} caracteres")
                    return texto
        except Exception as e:
            logger.warning(f"Erro ao extrair com PyPDF2: {e}")

        # Estratégia 3: OCR com Tesseract (para PDFs escaneados)
        if OCR_AVAILABLE:
            try:
                logger.info(f"Tentando OCR para {caminho_pdf.name}...")
                # Converte PDF para imagens
                images = convert_from_path(
                    caminho_pdf,
                    dpi=300,
                    first_page=1,
                    last_page=3,  # Limita a 3 páginas
                    poppler_path=POPPLER_PATH,
                )

                for i, image in enumerate(images):
                    logger.debug(f"Aplicando OCR na página {i+1}...")
                    texto_pagina = pytesseract.image_to_string(
                        image, lang="por"
                    )  # Português
                    if texto_pagina:
                        texto += texto_pagina + "\n"

                if texto.strip():
                    logger.info(f"Texto extraído com OCR: {len(texto)} caracteres")
                    return texto
            except Exception as e:
                logger.warning(f"Erro ao extrair com OCR: {e}")
        else:
            logger.warning(
                "OCR não disponível. Instale: pip install pytesseract pdf2image"
            )

        if not texto.strip():
            raise ValueError(
                "Não foi possível extrair texto do PDF. Pode ser imagem sem OCR."
            )

        return texto

    def processar_documento(self, caminho_pdf: Path) -> ProcessingResult:
        """
        Processa um documento PDF completo: extração, classificação e estruturação.

        Args:
            caminho_pdf: Caminho para o arquivo PDF

        Returns:
            ProcessingResult com status e dados extraídos
        """
        inicio = time.time()
        # Converter para Path se for string
        if isinstance(caminho_pdf, str):
            caminho_pdf = Path(caminho_pdf)
        nome_arquivo = caminho_pdf.name

        try:
            logger.info(f"Processando documento: {nome_arquivo}")

            # 1. Extração de texto
            texto = self.extrair_texto_pdf(caminho_pdf)

            if not texto.strip():
                raise ValueError("Documento vazio ou sem texto extraível")

            logger.debug(f"Texto extraído: {len(texto)} caracteres")

            # 2. Classificação do documento
            classificacao = self.llm_client.classificar_documento(texto)
            tipo_documento = classificacao.tipo

            logger.info(f"Documento classificado como: {tipo_documento}")

            # 3. Extração estruturada de dados
            dados_extraidos = self.llm_client.extrair_informacoes(texto, tipo_documento)

            tempo_total = time.time() - inicio

            logger.info(f"Documento processado com sucesso em {tempo_total:.2f}s")

            return ProcessingResult(
                arquivo=nome_arquivo,
                status="success",
                tipo_documento=tipo_documento,
                dados=dados_extraidos,
                tempo_processamento=tempo_total,
            )

        except Exception as e:
            tempo_total = time.time() - inicio
            logger.error(f"Erro ao processar {nome_arquivo}: {str(e)}")

            return ProcessingResult(
                arquivo=nome_arquivo,
                status="error",
                erro=str(e),
                tempo_processamento=tempo_total,
            )

    def validar_dados_extraidos(
        self, dados: Dict[str, Any], tipo_documento: str
    ) -> bool:
        """
        Valida se os dados extraídos estão completos e corretos.

        Args:
            dados: Dados extraídos
            tipo_documento: Tipo do documento

        Returns:
            True se válido, False caso contrário
        """
        # Validações básicas por tipo
        try:
            if tipo_documento == "nota_fiscal":
                return (
                    dados.get("fornecedor")
                    and dados.get("cnpj")
                    and dados.get("data_emissao")
                    and dados.get("itens")
                    and len(dados["itens"]) > 0
                    and dados.get("valor_total") is not None
                )

            elif tipo_documento == "contrato":
                return (
                    dados.get("contratante")
                    and dados.get("contratado")
                    and dados.get("objeto_contrato")
                    and dados.get("data_inicio_vigencia")
                    and dados.get("data_fim_vigencia")
                    and dados.get("valor_mensal") is not None
                )

            elif tipo_documento == "relatorio_manutencao":
                return (
                    dados.get("data")
                    and dados.get("tecnico_responsavel")
                    and dados.get("equipamento")
                    and dados.get("descricao_problema")
                    and dados.get("solucao_aplicada")
                )

            return False

        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False

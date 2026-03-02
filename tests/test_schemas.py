"""Testes para os schemas de dados."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.schemas import (Contrato, DocumentoClassificado, ItemNotaFiscal,
                         NotaFiscal, RelatorioManutencao)


class TestDocumentoClassificado:
    """Testes para DocumentoClassificado."""

    def test_classificacao_valida(self):
        """Testa classificação com dados válidos."""
        doc = DocumentoClassificado(tipo="nota_fiscal", confianca=0.95)
        assert doc.tipo == "nota_fiscal"
        assert doc.confianca == 0.95

    def test_confianca_default(self):
        """Testa valor default de confiança."""
        doc = DocumentoClassificado(tipo="contrato")
        assert doc.confianca == 1.0

    def test_confianca_invalida(self):
        """Testa validação de confiança fora do range."""
        with pytest.raises(ValidationError):
            DocumentoClassificado(tipo="nota_fiscal", confianca=1.5)

        with pytest.raises(ValidationError):
            DocumentoClassificado(tipo="nota_fiscal", confianca=-0.1)


class TestNotaFiscal:
    """Testes para NotaFiscal."""

    def test_nota_fiscal_completa(self):
        """Testa criação de nota fiscal completa."""
        nf = NotaFiscal(
            fornecedor="Empresa LTDA",
            cnpj="12.345.678/0001-90",
            data_emissao="2026-03-01",
            numero_nota="12345",
            itens=[
                ItemNotaFiscal(
                    descricao="Produto A",
                    quantidade=2.0,
                    valor_unitario=50.0,
                    valor_total=100.0,
                )
            ],
            valor_total=100.0,
        )

        assert nf.fornecedor == "Empresa LTDA"
        assert len(nf.itens) == 1
        assert nf.valor_total == 100.0

    def test_nota_fiscal_sem_opcionais(self):
        """Testa nota fiscal sem campos opcionais."""
        nf = NotaFiscal(
            fornecedor="Empresa",
            cnpj="12.345.678/0001-90",
            data_emissao="2026-03-01",
            itens=[],
            valor_total=0.0,
        )

        assert nf.numero_nota is None

    def test_item_nota_fiscal_valores(self):
        """Testa validação de valores de item."""
        item = ItemNotaFiscal(
            descricao="Produto", quantidade=10, valor_unitario=5.50, valor_total=55.00
        )

        assert item.quantidade == 10.0
        assert item.valor_unitario == 5.50


class TestContrato:
    """Testes para Contrato."""

    def test_contrato_completo(self):
        """Testa criação de contrato completo."""
        contrato = Contrato(
            contratante="Empresa A",
            contratado="Empresa B",
            objeto_contrato="Prestação de serviços de TI",
            data_inicio_vigencia="2026-01-01",
            data_fim_vigencia="2026-12-31",
            valor_mensal=5000.0,
            numero_contrato="CONT-2026-001",
        )

        assert contrato.contratante == "Empresa A"
        assert contrato.valor_mensal == 5000.0

    def test_contrato_sem_numero(self):
        """Testa contrato sem número."""
        contrato = Contrato(
            contratante="Empresa A",
            contratado="Empresa B",
            objeto_contrato="Serviços",
            data_inicio_vigencia="2026-01-01",
            data_fim_vigencia="2026-12-31",
            valor_mensal=1000.0,
        )

        assert contrato.numero_contrato is None


class TestRelatorioManutencao:
    """Testes para RelatorioManutencao."""

    def test_relatorio_completo(self):
        """Testa criação de relatório completo."""
        relatorio = RelatorioManutencao(
            data="2026-03-01",
            tecnico_responsavel="João Silva",
            equipamento="Impressora HP LaserJet",
            descricao_problema="Impressora não liga",
            solucao_aplicada="Substituição da fonte",
            numero_ordem_servico="OS-12345",
        )

        assert relatorio.tecnico_responsavel == "João Silva"
        assert relatorio.equipamento == "Impressora HP LaserJet"

    def test_relatorio_sem_os(self):
        """Testa relatório sem número de OS."""
        relatorio = RelatorioManutencao(
            data="2026-03-01",
            tecnico_responsavel="Maria",
            equipamento="Computador",
            descricao_problema="Problema",
            solucao_aplicada="Solução",
        )

        assert relatorio.numero_ordem_servico is None


class TestIntegracaoSchemas:
    """Testes de integração entre schemas."""

    def test_serialization_json(self):
        """Testa serialização para JSON."""
        doc = DocumentoClassificado(tipo="nota_fiscal", confianca=0.9)
        json_data = doc.model_dump()

        assert json_data == {"tipo": "nota_fiscal", "confianca": 0.9}

    def test_nested_validation(self):
        """Testa validação de estruturas aninhadas."""
        nf = NotaFiscal(
            fornecedor="Empresa",
            cnpj="12.345.678/0001-90",
            data_emissao="2026-03-01",
            itens=[
                ItemNotaFiscal(
                    descricao="Item 1", quantidade=1, valor_unitario=10, valor_total=10
                ),
                ItemNotaFiscal(
                    descricao="Item 2", quantidade=2, valor_unitario=20, valor_total=40
                ),
            ],
            valor_total=50.0,
        )

        assert len(nf.itens) == 2
        assert nf.itens[0].descricao == "Item 1"
        assert nf.itens[1].quantidade == 2.0

"""
Schemas para documentos processados usando Pydantic.
Define a estrutura de dados para cada tipo de documento.
"""

from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ItemNotaFiscal(BaseModel):
    """Item de uma nota fiscal."""

    descricao: str = Field(description="Descrição do item/produto")
    quantidade: float = Field(description="Quantidade do item")
    valor_unitario: Optional[float] = Field(None, description="Valor unitário do item")
    valor_total: float = Field(description="Valor total do item")


class NotaFiscal(BaseModel):
    """Schema para Nota Fiscal."""

    tipo_documento: Literal["nota_fiscal"] = "nota_fiscal"
    fornecedor: str = Field(description="Nome do fornecedor")
    cnpj: str = Field(description="CNPJ do fornecedor")
    data_emissao: str = Field(description="Data de emissão (formato: YYYY-MM-DD)")
    numero_nota: Optional[str] = Field(None, description="Número da nota fiscal")
    itens: List[ItemNotaFiscal] = Field(description="Lista de itens da nota fiscal")
    valor_total: float = Field(description="Valor total da nota fiscal")


class Contrato(BaseModel):
    """Schema para Contrato de Prestação de Serviços."""

    tipo_documento: Literal["contrato"] = "contrato"
    contratante: str = Field(description="Nome do contratante")
    contratado: str = Field(description="Nome do contratado")
    objeto_contrato: str = Field(description="Objeto/descrição do contrato")
    data_inicio_vigencia: str = Field(
        description="Data de início da vigência (formato: YYYY-MM-DD)"
    )
    data_fim_vigencia: str = Field(
        description="Data de fim da vigência (formato: YYYY-MM-DD)"
    )
    valor_mensal: float = Field(description="Valor mensal do contrato")
    numero_contrato: Optional[str] = Field(None, description="Número do contrato")


class RelatorioManutencao(BaseModel):
    """Schema para Relatório de Manutenção."""

    tipo_documento: Literal["relatorio_manutencao"] = "relatorio_manutencao"
    data: str = Field(description="Data da manutenção (formato: YYYY-MM-DD)")
    tecnico_responsavel: str = Field(description="Nome do técnico responsável")
    equipamento: str = Field(description="Nome/identificação do equipamento")
    descricao_problema: str = Field(description="Descrição do problema encontrado")
    solucao_aplicada: str = Field(description="Descrição da solução aplicada")
    numero_ordem_servico: Optional[str] = Field(
        None, description="Número da ordem de serviço"
    )


class DocumentoClassificado(BaseModel):
    """Resultado da classificação de um documento."""

    tipo: Literal["nota_fiscal", "contrato", "relatorio_manutencao"]
    confianca: float = Field(
        default=1.0, ge=0, le=1, description="Confiança da classificação (0-1)"
    )


class ProcessingResult(BaseModel):
    """Resultado do processamento de um documento."""

    arquivo: str = Field(description="Nome do arquivo processado")
    status: Literal["success", "error"] = Field(description="Status do processamento")
    tipo_documento: Optional[str] = Field(
        None, description="Tipo de documento identificado"
    )
    dados: Optional[dict] = Field(None, description="Dados extraídos do documento")
    erro: Optional[str] = Field(None, description="Mensagem de erro, se houver")
    tempo_processamento: Optional[float] = Field(
        None, description="Tempo de processamento em segundos"
    )


# Mapeamento de tipos para schemas
DOCUMENT_SCHEMAS = {
    "nota_fiscal": NotaFiscal,
    "contrato": Contrato,
    "relatorio_manutencao": RelatorioManutencao,
}

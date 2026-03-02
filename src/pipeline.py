"""
Pipeline principal de processamento de documentos.
Coordena a ingestão, classificação, extração e persistência dos dados.
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from tqdm import tqdm

from .document_processor import DocumentProcessor
from .llm_client import LLMClient
from .schemas import ProcessingResult

logger = logging.getLogger(__name__)


class DocumentPipeline:
    """Pipeline completo de processamento de documentos."""

    def __init__(
        self,
        input_dir: str,
        output_dir: str = "output",
        max_workers: int = 3,
        batch_size: int = 10,
    ):
        """
        Inicializa o pipeline.

        Args:
            input_dir: Diretório com os PDFs de entrada
            output_dir: Diretório para salvar os resultados
            max_workers: Número máximo de threads paralelas
            batch_size: Tamanho do batch para processamento
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.batch_size = batch_size

        # Cria diretório de saída se não existir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Inicializa componentes
        self.llm_client = LLMClient()
        self.processor = DocumentProcessor(self.llm_client)

        logger.info(f"Pipeline inicializado: input={input_dir}, output={output_dir}")

    def listar_arquivos_pdf(self) -> List[Path]:
        """
        Lista todos os arquivos PDF no diretório de entrada.

        Returns:
            Lista de caminhos para arquivos PDF
        """
        arquivos = list(self.input_dir.glob("*.pdf"))
        logger.info(f"Encontrados {len(arquivos)} arquivos PDF")
        return sorted(arquivos)

    def processar_lote(self, arquivos: List[Path]) -> List[ProcessingResult]:
        """
        Processa um lote de arquivos em paralelo.

        Args:
            arquivos: Lista de caminhos para arquivos PDF

        Returns:
            Lista de resultados do processamento
        """
        resultados = []

        # Processa com threads para I/O paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submete todas as tarefas
            futures = {
                executor.submit(self.processor.processar_documento, arquivo): arquivo
                for arquivo in arquivos
            }

            # Coleta resultados conforme completam (com barra de progresso)
            with tqdm(total=len(arquivos), desc="Processando", unit="doc") as pbar:
                for future in as_completed(futures):
                    try:
                        resultado = future.result()
                        resultados.append(resultado)
                    except Exception as e:
                        arquivo = futures[future]
                        logger.error(f"Erro crítico ao processar {arquivo.name}: {e}")
                        resultados.append(
                            ProcessingResult(
                                arquivo=arquivo.name,
                                status="error",
                                erro=f"Erro crítico: {str(e)}",
                            )
                        )
                    finally:
                        pbar.update(1)

        return resultados

    def salvar_resultados(self, resultados: List[ProcessingResult], timestamp: str):
        """
        Salva os resultados em múltiplos formatos.

        Args:
            resultados: Lista de resultados do processamento
            timestamp: Timestamp da execução
        """
        # 1. JSON consolidado
        json_path = self.output_dir / f"resultados_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(
                [r.model_dump() for r in resultados], f, indent=2, ensure_ascii=False
            )
        logger.info(f"Resultados salvos em JSON: {json_path}")

        # 2. JSONs individuais por tipo de documento
        por_tipo = {}
        for resultado in resultados:
            if resultado.status == "success" and resultado.tipo_documento:
                tipo = resultado.tipo_documento
                if tipo not in por_tipo:
                    por_tipo[tipo] = []
                por_tipo[tipo].append(resultado.dados)

        for tipo, documentos in por_tipo.items():
            tipo_path = self.output_dir / f"{tipo}_{timestamp}.json"
            with open(tipo_path, "w", encoding="utf-8") as f:
                json.dump(documentos, f, indent=2, ensure_ascii=False)
            logger.info(f"Documentos do tipo '{tipo}' salvos em: {tipo_path}")

        # 3. CSV com resumo do processamento
        csv_data = []
        for resultado in resultados:
            csv_data.append(
                {
                    "arquivo": resultado.arquivo,
                    "status": resultado.status,
                    "tipo_documento": resultado.tipo_documento or "N/A",
                    "tempo_processamento": (
                        f"{resultado.tempo_processamento:.2f}s"
                        if resultado.tempo_processamento
                        else "N/A"
                    ),
                    "erro": resultado.erro or "",
                }
            )

        df = pd.DataFrame(csv_data)
        csv_path = self.output_dir / f"resumo_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info(f"Resumo salvo em CSV: {csv_path}")

        # 4. Relatório de estatísticas
        stats_path = self.output_dir / f"estatisticas_{timestamp}.txt"
        self._gerar_relatorio_estatisticas(resultados, stats_path)

    def _gerar_relatorio_estatisticas(
        self, resultados: List[ProcessingResult], output_path: Path
    ):
        """
        Gera relatório com estatísticas do processamento.

        Args:
            resultados: Lista de resultados
            output_path: Caminho para salvar o relatório
        """
        total = len(resultados)
        sucessos = sum(1 for r in resultados if r.status == "success")
        erros = total - sucessos

        # Contagem por tipo
        por_tipo = {}
        for resultado in resultados:
            if resultado.status == "success" and resultado.tipo_documento:
                tipo = resultado.tipo_documento
                por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

        # Tempo médio
        tempos = [r.tempo_processamento for r in resultados if r.tempo_processamento]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("RELATÓRIO DE PROCESSAMENTO DE DOCUMENTOS\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Total de documentos processados: {total}\n")
            f.write(f"Sucessos: {sucessos} ({sucessos/total*100:.1f}%)\n")
            f.write(f"Erros: {erros} ({erros/total*100:.1f}%)\n\n")

            f.write("Documentos por tipo:\n")
            for tipo, count in sorted(por_tipo.items()):
                f.write(f"  - {tipo}: {count}\n")
            f.write("\n")

            f.write(f"Tempo médio de processamento: {tempo_medio:.2f}s\n")
            f.write(f"Tempo total: {sum(tempos):.2f}s\n\n")

            if erros > 0:
                f.write("Documentos com erro:\n")
                for resultado in resultados:
                    if resultado.status == "error":
                        f.write(f"  - {resultado.arquivo}: {resultado.erro}\n")

        logger.info(f"Relatório de estatísticas salvo: {output_path}")

    def executar(self):
        """
        Executa o pipeline completo de processamento.
        """
        inicio = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info("=" * 60)
        logger.info("INICIANDO PIPELINE DE PROCESSAMENTO")
        logger.info("=" * 60)

        # 1. Listar arquivos
        arquivos = self.listar_arquivos_pdf()

        if not arquivos:
            logger.warning("Nenhum arquivo PDF encontrado!")
            return

        # 2. Processar em lotes
        todos_resultados = []
        for i in range(0, len(arquivos), self.batch_size):
            lote = arquivos[i : i + self.batch_size]
            logger.info(
                f"Processando lote {i//self.batch_size + 1} ({len(lote)} arquivos)"
            )
            resultados_lote = self.processar_lote(lote)
            todos_resultados.extend(resultados_lote)

        # 3. Salvar resultados
        logger.info("Salvando resultados...")
        self.salvar_resultados(todos_resultados, timestamp)

        # 4. Resumo final
        tempo_total = time.time() - inicio
        sucessos = sum(1 for r in todos_resultados if r.status == "success")

        logger.info("=" * 60)
        logger.info("PIPELINE CONCLUÍDO")
        logger.info(f"Tempo total: {tempo_total:.2f}s")
        logger.info(f"Documentos processados: {len(todos_resultados)}")
        logger.info(f"Sucessos: {sucessos}")
        logger.info(f"Erros: {len(todos_resultados) - sucessos}")
        logger.info(f"Resultados salvos em: {self.output_dir}")
        logger.info("=" * 60)

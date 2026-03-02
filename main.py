"""
Ponto de entrada principal do pipeline de processamento de documentos.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import DocumentPipeline
from src.config import configurar_logging

logger = logging.getLogger(__name__)


def validar_configuracao():
    """Valida se todas as configurações necessárias estão presentes."""
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY não configurada!")
        logger.error("Configure no arquivo .env ou como variável de ambiente")
        sys.exit(1)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Pipeline de processamento de documentos com LLM"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/raw",
        help="Diretório com os PDFs de entrada (padrão: data/raw)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Diretório para salvar os resultados (padrão: output)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Número máximo de threads paralelas (padrão: 3)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Tamanho do batch para processamento (padrão: 10)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nível de logging (padrão: INFO)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Arquivo para salvar logs (opcional)"
    )
    
    args = parser.parse_args()
    
    # Configura logging
    configurar_logging(nivel=args.log_level, log_file=args.log_file)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    logger.info("Iniciando aplicação de processamento de documentos")
    logger.info(f"Python version: {sys.version}")
    
    # Valida configuração
    validar_configuracao()
    
    # Verifica se diretório de entrada existe
    input_path = Path(args.input_dir)
    if not input_path.exists():
        logger.error(f"Diretório de entrada não encontrado: {input_path}")
        sys.exit(1)
    
    try:
        # Cria e executa pipeline
        pipeline = DocumentPipeline(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            max_workers=args.max_workers,
            batch_size=args.batch_size
        )
        
        pipeline.executar()
        
        logger.info("Aplicação concluída com sucesso!")
        
    except KeyboardInterrupt:
        logger.warning("Processamento interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

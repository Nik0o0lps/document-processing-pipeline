"""
Configuração do sistema de logging.
"""

import logging
import sys
from pathlib import Path

import colorlog


def configurar_logging(nivel: str = "INFO", log_file: str = None):
    """
    Configura o sistema de logging com cores e formato apropriado.

    Args:
        nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Caminho para arquivo de log (opcional)
    """
    # Remove handlers existentes
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Define formato
    log_format = "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Handler para console com cores
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    # Configura root logger
    root.setLevel(getattr(logging, nivel.upper()))
    root.addHandler(console_handler)

    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root.addHandler(file_handler)

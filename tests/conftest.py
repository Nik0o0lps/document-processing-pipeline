"""Configuração compartilhada para todos os testes."""

import sys
from pathlib import Path

import pytest

# Adiciona o diretório raiz ao path para imports
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture(scope="session")
def project_root():
    """Retorna o diretório raiz do projeto."""
    return root_dir


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Retorna o diretório de dados de teste."""
    return project_root / "tests" / "data"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture para mockar variáveis de ambiente."""

    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)

    return _set_env


# Configuração de logging para testes
pytest.register_assert_rewrite("tests")

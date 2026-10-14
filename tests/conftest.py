"""Fixtures dos cenários de aceite (spec seções 8 e 14.2)."""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

# Permite `from src...` ao rodar `pytest` a partir da raiz do repositório.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.exceptions import (  # noqa: E402
    CampoObrigatorioAusenteError,
    IdentificadorInvalidoError,
    TipoDadoInvalidoError,
    ValorEnumInvalidoError,
)

_BASE = datetime(2026, 1, 5, 9, 0, tzinfo=UTC)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Informa o início da execução da suíte."""
    print("\n>>> Iniciando execução dos testes do SDD Task Analyser...")


def pytest_terminal_summary(terminalreporter: Any) -> None:
    """Informa a finalização da suíte com a quantidade de testes que passaram."""
    passaram = len(terminalreporter.stats.get("passed", []))
    falharam = len(terminalreporter.stats.get("failed", [])) + len(
        terminalreporter.stats.get("error", [])
    )
    total = passaram + falharam
    terminalreporter.write_line(
        f">>> Execução finalizada: {passaram}/{total} testes passaram.", bold=True
    )


def _tarefa(
    id_tarefa: int,
    prioridade: str,
    duracao_min: int,
    prazo_min: int,
    status: str = "concluída",
) -> dict[str, Any]:
    """Cria tarefa iniciada em `_BASE`, concluída após `duracao_min`."""
    concluida = status == "concluída"
    return {
        "id_tarefa": id_tarefa,
        "data_criacao": _BASE - timedelta(days=1),
        "data_inicio": _BASE if concluida else None,
        "data_conclusao": _BASE + timedelta(minutes=duracao_min) if concluida else None,
        "prazo": _BASE + timedelta(minutes=prazo_min),
        "prioridade": prioridade,
        "status": status,
    }


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    """Cinco tarefas concluídas válidas (duração/prazo em minutos a partir de 09:00).

    alta: 60 (prazo 120, no prazo) e 120 (prazo 90, atrasada)
    média: 30 (prazo 180, no prazo)
    baixa: 180 (prazo 120, atrasada) e 90 (prazo 90, conclusão == prazo, no prazo)
    """
    return [
        _tarefa(1, "alta", 60, 120),
        _tarefa(2, "alta", 120, 90),
        _tarefa(3, "média", 30, 180),
        _tarefa(4, "baixa", 180, 120),
        _tarefa(5, "baixa", 90, 90),
    ]


@pytest.fixture
def tarefas_com_descartes(tarefas_validas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """`tarefas_validas` acrescida de tarefas que devem ser excluídas da análise."""
    conclusao_antes_do_inicio = _tarefa(10, "alta", -30, 120)
    concluida_sem_datas = _tarefa(11, "média", 0, 120)
    concluida_sem_datas["data_inicio"] = None
    concluida_sem_datas["data_conclusao"] = None
    return tarefas_validas + [
        conclusao_antes_do_inicio,
        concluida_sem_datas,
        _tarefa(12, "baixa", 0, 120, status="pendente"),
        _tarefa(13, "alta", 0, 120, status="cancelada"),
    ]


@pytest.fixture
def tarefas_com_entrada_invalida() -> list[tuple[dict[str, Any], type[Exception]]]:
    """Pares (tarefa estruturalmente inválida, exceção esperada)."""
    base = _tarefa(1, "alta", 60, 120)

    def variante(**alteracoes: Any) -> dict[str, Any]:
        return {**base, **alteracoes}

    sem_prazo = {chave: v for chave, v in base.items() if chave != "prazo"}
    return [
        (sem_prazo, CampoObrigatorioAusenteError),
        (variante(status=None), CampoObrigatorioAusenteError),
        (variante(id_tarefa="abc"), TipoDadoInvalidoError),
        (variante(prazo="2026-01-05"), TipoDadoInvalidoError),
        (variante(prioridade="urgente"), ValorEnumInvalidoError),
        (variante(status="em andamento"), ValorEnumInvalidoError),
        (variante(id_tarefa=0), IdentificadorInvalidoError),
        (variante(id_tarefa=-3), IdentificadorInvalidoError),
    ]


@pytest.fixture
def tarefas_sem_concluidas() -> list[dict[str, Any]]:
    """Tarefas apenas pendentes e canceladas."""
    return [
        _tarefa(1, "alta", 0, 120, status="pendente"),
        _tarefa(2, "baixa", 0, 120, status="cancelada"),
    ]

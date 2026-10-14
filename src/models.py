"""Modelos de dados de entrada do Task Analyser (contrato: spec seção 11.1)."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Prioridade(str, Enum):
    """Prioridade de uma tarefa (spec seção 11.1)."""

    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"


class Status(str, Enum):
    """Status de uma tarefa (spec seção 11.1)."""

    CONCLUIDA = "concluída"
    PENDENTE = "pendente"
    CANCELADA = "cancelada"


@dataclass
class Tarefa:
    """Representa uma tarefa de entrada, conforme contrato (spec seção 11.1).

    Attributes:
        id_tarefa: Identificador único da tarefa (> 0).
        data_criacao: Data/hora de criação (UTC).
        prazo: Data/hora limite para conclusão (UTC).
        prioridade: Prioridade da tarefa.
        status: Status da tarefa.
        data_inicio: Data/hora de início; obrigatória quando concluída.
        data_conclusao: Data/hora de conclusão; obrigatória quando concluída.
    """

    id_tarefa: int
    data_criacao: datetime
    prazo: datetime
    prioridade: Prioridade
    status: Status
    data_inicio: datetime | None = None
    data_conclusao: datetime | None = None

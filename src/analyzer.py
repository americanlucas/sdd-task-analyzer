"""Cálculo dos indicadores de produtividade (contrato: spec seção 11)."""

import logging
from collections.abc import Iterable, Mapping
from dataclasses import asdict
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from src.exceptions import (
    CampoObrigatorioAusenteError,
    IdentificadorInvalidoError,
    TipoDadoInvalidoError,
    ValorEnumInvalidoError,
)
from src.models import Prioridade, Status, Tarefa

logger = logging.getLogger(__name__)

_CAMPOS_OBRIGATORIOS = ("id_tarefa", "data_criacao", "prazo", "prioridade", "status")
_CAMPOS_DATA = ("data_criacao", "prazo", "data_inicio", "data_conclusao")
_SEGUNDOS_POR_MINUTO = 60


def _normalizar_utc(valor: datetime) -> datetime:
    """Converte para UTC; datetimes sem fuso são interpretados como UTC."""
    if valor.tzinfo is None:
        return valor.replace(tzinfo=UTC)
    return valor.astimezone(UTC)


def _converter_enum(
    enum_cls: type[Enum], campo: str, valor: Any, id_tarefa: Any
) -> Any:
    """Converte `valor` para o membro de `enum_cls` ou lança a exceção adequada."""
    if not isinstance(valor, str):
        raise TipoDadoInvalidoError(campo, "deve ser texto", id_tarefa)
    try:
        return enum_cls(valor)
    except ValueError:
        permitidos = ", ".join(membro.value for membro in enum_cls)
        raise ValorEnumInvalidoError(
            campo, f"possui valor '{valor}' fora dos permitidos ({permitidos})", id_tarefa
        ) from None


def _validar_campos_basicos(dados: Mapping[str, Any]) -> None:
    """Valida presença, tipo e valor de `id_tarefa` e dos campos obrigatórios."""
    id_tarefa = dados.get("id_tarefa")
    for campo in _CAMPOS_OBRIGATORIOS:
        if dados.get(campo) is None:
            raise CampoObrigatorioAusenteError(campo, "é obrigatório e está ausente", id_tarefa)
    if isinstance(id_tarefa, bool) or not isinstance(id_tarefa, int):
        raise TipoDadoInvalidoError("id_tarefa", "deve ser um inteiro", id_tarefa)
    if id_tarefa <= 0:
        raise IdentificadorInvalidoError("id_tarefa", "deve ser maior que zero", id_tarefa)
    for campo in _CAMPOS_DATA:
        valor = dados.get(campo)
        if valor is not None and not isinstance(valor, datetime):
            raise TipoDadoInvalidoError(campo, "deve ser datetime", id_tarefa)


def _validar_tarefa(entrada: Tarefa | Mapping[str, Any]) -> Tarefa:
    """Valida a entrada e a converte em `Tarefa` com datas normalizadas em UTC.

    Args:
        entrada: `Tarefa` ou mapeamento com os campos do contrato (seção 11.1).

    Returns:
        Tarefa validada.

    Raises:
        CampoObrigatorioAusenteError: Campo obrigatório ausente ou nulo.
        TipoDadoInvalidoError: Campo com tipo incompatível.
        IdentificadorInvalidoError: `id_tarefa` <= 0.
        ValorEnumInvalidoError: `prioridade` ou `status` inválidos.
    """
    dados = asdict(entrada) if isinstance(entrada, Tarefa) else dict(entrada)
    _validar_campos_basicos(dados)
    id_tarefa = dados["id_tarefa"]
    prioridade = _converter_enum(Prioridade, "prioridade", dados["prioridade"], id_tarefa)
    status = _converter_enum(Status, "status", dados["status"], id_tarefa)
    datas = {
        campo: _normalizar_utc(dados[campo]) if dados.get(campo) is not None else None
        for campo in _CAMPOS_DATA
    }
    return Tarefa(
        id_tarefa=id_tarefa, prioridade=prioridade, status=status, **datas
    )


def _eh_analisavel(tarefa: Tarefa) -> bool:
    """Indica se a tarefa entra nos cálculos (regras 1, 4, 5 e 9 da seção 11.3)."""
    if tarefa.status is not Status.CONCLUIDA:
        return False
    if tarefa.data_inicio is None or tarefa.data_conclusao is None:
        logger.warning("Tarefa %s ignorada: datas de início/conclusão ausentes", tarefa.id_tarefa)
        return False
    if tarefa.data_conclusao < tarefa.data_inicio:
        logger.warning("Tarefa %s ignorada: conclusão anterior ao início", tarefa.id_tarefa)
        return False
    return True


def _tempo_conclusao_min(tarefa: Tarefa) -> float:
    """Retorna `data_conclusao - data_inicio` em minutos (regra 2)."""
    delta = tarefa.data_conclusao - tarefa.data_inicio  # type: ignore[operator]
    return delta.total_seconds() / _SEGUNDOS_POR_MINUTO


def _esta_atrasada(tarefa: Tarefa) -> bool:
    """Indica atraso: `data_conclusao > prazo` (regra 3)."""
    return tarefa.data_conclusao > tarefa.prazo  # type: ignore[operator]


def _calcular_indicadores(tarefas: list[Tarefa]) -> dict[str, float | int]:
    """Calcula os indicadores de um grupo; grupo vazio retorna zeros (regras 6 e 8)."""
    quantidade = len(tarefas)
    if quantidade == 0:
        return {
            "tempo_medio_conclusao_min": 0.0,
            "taxa_atraso_percentual": 0.0,
            "quantidade_tarefas": 0,
        }
    tempo_medio = sum(_tempo_conclusao_min(t) for t in tarefas) / quantidade
    atrasadas = sum(1 for t in tarefas if _esta_atrasada(t))
    return {
        "tempo_medio_conclusao_min": round(tempo_medio, 2),
        "taxa_atraso_percentual": round(atrasadas / quantidade * 100, 2),
        "quantidade_tarefas": quantidade,
    }


def analisar_tarefas(tarefas: Iterable[Tarefa | Mapping[str, Any]]) -> dict[str, Any]:
    """Calcula os indicadores de produtividade de um conjunto de tarefas.

    Todas as tarefas são validadas; depois, somente as concluídas e com datas
    coerentes entram nos cálculos (spec seção 11.3).

    Args:
        tarefas: Tarefas como `Tarefa` ou mapeamentos com os campos do contrato.

    Returns:
        Dicionário com `tempo_medio_conclusao_min`, `taxa_atraso_percentual`,
        `quantidade_tarefas` e `indicadores_por_prioridade` (chaves `baixa`,
        `média` e `alta`, sempre presentes).

    Raises:
        TaskValidationError: Subclasse específica para entrada inválida (seção 11.4).
    """
    validadas = [_validar_tarefa(entrada) for entrada in tarefas]
    analisaveis = [t for t in validadas if _eh_analisavel(t)]
    resultado: dict[str, Any] = _calcular_indicadores(analisaveis)
    resultado["indicadores_por_prioridade"] = {
        prioridade.value: _calcular_indicadores(
            [t for t in analisaveis if t.prioridade is prioridade]
        )
        for prioridade in Prioridade
    }
    logger.info("Análise concluída: %d tarefas consideradas", len(analisaveis))
    return resultado


analyse_tasks = analisar_tarefas

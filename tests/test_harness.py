"""Test harness dos cenários de aceite (spec seção 8) e da API pública."""

from datetime import UTC, datetime
from typing import Any

import pytest

from src.analyzer import analisar_tarefas, analyse_tasks
from src.exceptions import (
    CampoObrigatorioAusenteError,
    IdentificadorInvalidoError,
    TaskValidationError,
    TipoDadoInvalidoError,
    ValorEnumInvalidoError,
)
from src.models import Prioridade, Status, Tarefa

INDICADORES_ZERADOS = {
    "tempo_medio_conclusao_min": 0.0,
    "taxa_atraso_percentual": 0.0,
    "quantidade_tarefas": 0,
}

# Calculado manualmente a partir de `tarefas_validas`:
# tempos 60+120+30+180+90 = 480 min / 5 = 96.0; atrasadas 2/5 = 40.0%.
RESULTADO_ESPERADO: dict[str, Any] = {
    "tempo_medio_conclusao_min": 96.0,
    "taxa_atraso_percentual": 40.0,
    "quantidade_tarefas": 5,
    "indicadores_por_prioridade": {
        "alta": {
            "tempo_medio_conclusao_min": 90.0,
            "taxa_atraso_percentual": 50.0,
            "quantidade_tarefas": 2,
        },
        "média": {
            "tempo_medio_conclusao_min": 30.0,
            "taxa_atraso_percentual": 0.0,
            "quantidade_tarefas": 1,
        },
        "baixa": {
            "tempo_medio_conclusao_min": 135.0,
            "taxa_atraso_percentual": 50.0,
            "quantidade_tarefas": 2,
        },
    },
}


def test_analisar_tarefas_cenario_1_sucesso_geral(tarefas_validas):
    resultado = analisar_tarefas(tarefas_validas)

    assert resultado["tempo_medio_conclusao_min"] == 96.0
    assert resultado["taxa_atraso_percentual"] == 40.0
    assert resultado["quantidade_tarefas"] == 5


def test_analisar_tarefas_cenario_2_sucesso_por_prioridade(tarefas_validas):
    resultado = analisar_tarefas(tarefas_validas)

    assert resultado["indicadores_por_prioridade"] == RESULTADO_ESPERADO[
        "indicadores_por_prioridade"
    ]


def test_analisar_tarefas_cenario_3_erro_entrada_invalida(tarefas_com_entrada_invalida):
    for tarefa, excecao in tarefas_com_entrada_invalida:
        with pytest.raises(excecao):
            analisar_tarefas([tarefa])


def test_analisar_tarefas_cenario_4_borda_sem_concluidas(tarefas_sem_concluidas):
    resultado = analisar_tarefas(tarefas_sem_concluidas)

    assert {k: resultado[k] for k in INDICADORES_ZERADOS} == INDICADORES_ZERADOS
    for prioridade in ("baixa", "média", "alta"):
        assert resultado["indicadores_por_prioridade"][prioridade] == INDICADORES_ZERADOS


def test_lista_vazia_retorna_indicadores_zerados():
    resultado = analisar_tarefas([])

    assert resultado["quantidade_tarefas"] == 0
    assert resultado["tempo_medio_conclusao_min"] == 0.0


def test_tarefas_inconsistentes_ou_nao_concluidas_sao_excluidas(tarefas_com_descartes):
    assert analisar_tarefas(tarefas_com_descartes) == RESULTADO_ESPERADO


def test_aceita_instancias_de_tarefa(tarefas_validas):
    tarefas = [
        Tarefa(
            **{**dados, "prioridade": Prioridade(dados["prioridade"]), "status": Status(dados["status"])}
        )
        for dados in tarefas_validas
    ]

    assert analisar_tarefas(tarefas) == RESULTADO_ESPERADO


def test_datas_sem_fuso_sao_interpretadas_como_utc(tarefas_validas):
    ingenuas = [
        {
            **t,
            **{
                campo: t[campo].astimezone(UTC).replace(tzinfo=None)
                for campo in ("data_criacao", "data_inicio", "data_conclusao", "prazo")
            },
        }
        for t in tarefas_validas
    ]

    assert analisar_tarefas(ingenuas) == RESULTADO_ESPERADO


def test_arredondamento_em_duas_casas(tarefas_validas):
    tarefas = tarefas_validas[:3]  # alta 60, alta 120 (atrasada), média 30
    tarefas[0]["data_conclusao"] = tarefas[0]["data_inicio"].replace(minute=20)  # 20 min

    resultado = analisar_tarefas(tarefas)

    assert resultado["tempo_medio_conclusao_min"] == 56.67  # (20+120+30)/3
    assert resultado["taxa_atraso_percentual"] == 33.33


def test_alias_analyse_tasks_aponta_para_analisar_tarefas():
    assert analyse_tasks is analisar_tarefas


def test_excecoes_herdam_de_task_validation_error():
    for excecao in (
        CampoObrigatorioAusenteError,
        TipoDadoInvalidoError,
        ValorEnumInvalidoError,
        IdentificadorInvalidoError,
    ):
        assert issubclass(excecao, TaskValidationError)


def test_mensagem_de_erro_indica_tarefa_e_campo():
    tarefa = {
        "id_tarefa": 7,
        "data_criacao": datetime(2026, 1, 1, tzinfo=UTC),
        "prazo": datetime(2026, 1, 2, tzinfo=UTC),
        "prioridade": "urgente",
        "status": "pendente",
    }

    with pytest.raises(ValorEnumInvalidoError, match=r"Tarefa 7.*'prioridade'"):
        analisar_tarefas([tarefa])

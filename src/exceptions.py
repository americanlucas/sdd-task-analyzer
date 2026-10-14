"""Taxonomia de exceções do Task Analyser (spec seção 11.4).

Todas herdam de `TaskValidationError`, o que permite capturar qualquer erro
de validação de entrada com um único `except`.
"""


class TaskValidationError(Exception):
    """Erro base para entrada estruturalmente inválida.

    Attributes:
        campo: Nome do campo afetado.
        id_tarefa: Identificador da tarefa afetada, quando conhecido.
    """

    def __init__(self, campo: str, detalhe: str, id_tarefa: object = None) -> None:
        """Monta a mensagem indicando tarefa e campo afetados.

        Args:
            campo: Nome do campo afetado.
            detalhe: Descrição do problema encontrado.
            id_tarefa: Identificador da tarefa, se disponível.
        """
        self.campo = campo
        self.id_tarefa = id_tarefa
        origem = f"Tarefa {id_tarefa}" if id_tarefa is not None else "Tarefa sem id"
        super().__init__(f"{origem}: campo '{campo}' {detalhe}")


class CampoObrigatorioAusenteError(TaskValidationError):
    """Campo obrigatório ausente ou nulo."""


class TipoDadoInvalidoError(TaskValidationError):
    """Campo com tipo incompatível com o contrato."""


class ValorEnumInvalidoError(TaskValidationError):
    """`prioridade` ou `status` fora dos valores permitidos."""


class IdentificadorInvalidoError(TaskValidationError):
    """`id_tarefa` menor ou igual a zero."""

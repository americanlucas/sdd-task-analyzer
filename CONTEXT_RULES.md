# Regras de Contexto — SDD Task Analyser

> Fonte de verdade: `specs/task_analyser_spec.md`. Este arquivo apenas consolida, de forma consultável, as regras que o agente de IA deve seguir durante a geração de código. Em caso de divergência, o spec prevalece.

## Diretrizes Obrigatórias

(spec seção 9.1)

- Python 3.11+ como versão mínima obrigatória
- *Type hints* (anotações de tipo) em todas as funções e métodos
- Princípio Single Responsibility (SRP) e código limpo (PEP 8)
- Documentação formal no padrão Google style docstrings para módulos, classes, funções e parâmetros
- Funções pequenas, coesas e com um único propósito
- Tratamento de exceções específico (taxonomia da seção 11.4 do spec) e com mensagens claras
- Logs estruturados utilizando o módulo padrão `logging`
- Código legível, manutenível, com nomes de variáveis e funções descritivos

## Restrições

(spec seção 9.2)

- Não utilizar bibliotecas externas não autorizadas (fora da stack da seção 6 do spec)
- Não alterar, remover ou adaptar os cenários de teste fornecidos (seção 8 do spec)
- Não modificar a estrutura de pastas definida no spec (seção 10)
- Não persistir dados em arquivos ou bancos de dados (fora do escopo, seção 2.2)
- Não alterar a assinatura (nome e parâmetros) das funções públicas sem autorização (ex.: `analisar_tarefas`, seção 14.2)
- Não gerar código sem testes correspondentes para as novas funcionalidades
- Não inserir código duplicado ou sem necessidade
- Não assumir comportamentos não especificados no contrato de negócio (seção 11)

## Stack Autorizada

(spec seção 6.2 — nenhuma lib fora desta lista)

| Biblioteca | Categoria | Uso no projeto |
| :---- | :---- | :---- |
| `datetime` (stdlib) | Manipulação de data/hora | Cálculo de tempo de conclusão e verificação de atraso (UTC) |
| `dataclasses` (stdlib) | Modelagem de dados | Representação tipada da entidade `Tarefa` |
| `typing` / `enum` (stdlib) | Tipagem estática | Anotações de tipo e enums de `prioridade`/`status` |
| `logging` (stdlib) | Observabilidade | Logs estruturados exigidos pela governança (seção 9.1) |
| `pytest` | Testes automatizados | Implementação do test harness (seção 8) |

Nenhuma dependência externa de terceiros (ex.: `pandas`, frameworks web) é necessária ou autorizada nesta etapa. A solução deve ser resolvida com biblioteca padrão + `pytest`. Toda dependência deve constar em `requirements.txt`.

## Regras de Negócio

(spec seção 11.3 — contrato executável; RF05, RF06, RF08–RF11)

1. Considerar **apenas** tarefas com `status = 'concluída'` para cálculo de tempo e atraso.
2. `tempo_conclusao = data_conclusao − data_inicio` (em minutos).
3. Tarefa em **atraso** quando `data_conclusao > prazo`.
4. **Ignorar** tarefas com datas inconsistentes (ex.: `data_conclusao` anterior a `data_inicio`).
5. **Ignorar** tarefas com `status = 'concluída'` que não possuam `data_inicio` e/ou `data_conclusao` preenchidas — tratamento idêntico à regra 4, sem gerar exceção.
6. Divisão por zero deve ser **tratada** quando não houver tarefas concluídas (retornar indicadores zerados de forma consistente, sem erro).
7. Fuso horário sempre **UTC**.
8. Arredondamento: **2 casas decimais** para tempos e percentuais.
9. Tarefas com `status = 'pendente'` ou `'cancelada'` são **totalmente excluídas** da análise — não entram em `quantidade_tarefas`, nem em nenhum contador ou indicador de saída, geral ou por prioridade.

### Saídas esperadas

(spec seção 11.2)

| Campo | Tipo | Descrição |
| :---- | :---- | :---- |
| `tempo_medio_conclusao_min` | `float` | Tempo médio de conclusão em minutos (por prioridade e geral) |
| `taxa_atraso_percentual` | `float` | Percentual de tarefas concluídas após o prazo (por prioridade e geral) |
| `quantidade_tarefas` | `int` | Total de tarefas consideradas na análise (por prioridade e geral) |
| `indicadores_por_prioridade` | `dict` | Estrutura com métricas agrupadas por prioridade (`baixa`, `média`, `alta`) |

## Taxonomia de Exceções

(spec seção 11.4)

Cada exceção deve trazer mensagem clara indicando o campo/tarefa afetada (RNF05). Inconsistências de data (regras 4 e 5 da seção 11.3) **não** geram exceção — são silenciosamente ignoradas. Exceções são reservadas para entrada estruturalmente inválida.

| Exceção | Quando disparar |
| :---- | :---- |
| `CampoObrigatorioAusenteError` | Campo obrigatório (`id_tarefa`, `data_criacao`, `prazo`, `prioridade`, `status`) ausente ou nulo |
| `TipoDadoInvalidoError` | Campo com tipo incompatível com o contrato (ex.: `id_tarefa` não numérico) |
| `ValorEnumInvalidoError` | `prioridade` ou `status` fora dos valores permitidos (seção 11.1) |
| `IdentificadorInvalidoError` | `id_tarefa` ≤ 0 |

## Checklist de Homologação

(spec seção 10.1 — ordem obrigatória antes de qualquer commit do código gerado)

1. Execução completa dos testes automatizados (validação funcional)
2. Revisão de conformidade com `CONTEXT_RULES.md`
3. Análise de qualidade de código e tratamento de erros
4. Testes manuais em casos de borda
5. **Somente após aprovação** o código é commitado
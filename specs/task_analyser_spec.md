# Especificação Técnica — SDD Task Analyser

## 1\. Visão Geral

### 1.1 Descrição do Sistema

Aplicação de **análise de tarefas e produtividade**, que transforma um conjunto bruto de tarefas em indicadores objetivos de desempenho, servindo como ferramenta de apoio à decisão para times e indivíduos que precisam entender **como** e **quão bem** o trabalho está sendo executado.

**Objetivos do sistema:**

- **Medir eficiência de execução** — quantificar quanto tempo, em média, uma tarefa leva do início até a conclusão, permitindo identificar se o ritmo de entrega está dentro do esperado.  
- **Diagnosticar cumprimento de prazos** — apurar a taxa de atraso das entregas, expondo o quanto o planejamento (prazo) diverge da execução real (data de conclusão).  
- **Segmentar desempenho por criticidade** — ao agrupar os indicadores por prioridade (`baixa`, `média`, `alta`), o sistema permite enxergar se tarefas mais críticas são de fato tratadas com mais agilidade, ou se o inverso ocorre (um sinal de gargalo ou má priorização).  
- **Oferecer uma base confiável e auditável** — todos os cálculos seguem regras de negócio explícitas e determinísticas (seção 11.3), tornando os indicadores reprodutíveis e rastreáveis, sem "caixas-pretas".  
- **Servir de fundação extensível** — a arquitetura e o contrato de dados são desenhados para suportar, em etapas futuras, novas dimensões de análise (por período, por responsável, por categoria) sem quebrar o contrato já estabelecido.

Em suma, o sistema não apenas soma e divide números — ele existe para responder, com dados, três perguntas centrais de gestão: *o time está rápido? está pontual? está priorizando corretamente?*

### 1.2 Leque de Tarefas Analíticas

Sobre o mesmo conjunto de dados de entrada (seção 11.1), o sistema é capaz de derivar as seguintes análises:

| Análise | O que responde |
| :---- | :---- |
| Tempo médio de conclusão (geral) | Qual o tempo médio de execução de todas as tarefas concluídas? |
| Tempo médio de conclusão (por prioridade) | Tarefas de alta prioridade são concluídas mais rápido que as de baixa? |
| Taxa de atraso (geral) | Qual proporção do total de entregas ultrapassa o prazo? |
| Taxa de atraso (por prioridade) | O atraso é mais frequente em tarefas críticas ou triviais? |
| Quantidade de tarefas consideradas (geral e por prioridade) | Qual o volume de trabalho efetivamente concluído e analisado, por segmento? |
| Distribuição de indicadores por prioridade | Como o desempenho se compara entre os três níveis de prioridade, lado a lado? |
| Detecção e descarte de inconsistências | Quais tarefas possuem dados inválidos (datas incoerentes) e foram excluídas da análise? |

### 1.3 Papel deste Documento

Este documento é o **contrato executável** entre a especificação e o código gerado na próxima etapa. Toda geração automática de código (via assistente de IA \+ pipeline CI/CD) deve seguir **estritamente** os inputs, outputs, tipos de dados e regras de negócio aqui definidos — não há margem de interpretação livre por parte do agente gerador.

---

## 2\. Escopo do Projeto

### 2.1 Dentro do Escopo

- Cálculo de tempo médio de conclusão (geral e por prioridade)  
- Cálculo de taxa de atraso (geral e por prioridade)  
- Contagem de tarefas consideradas na análise (geral e por prioridade)  
- Agrupamento e comparação de indicadores por prioridade (`baixa`, `média`, `alta`)  
- Identificação de tarefas em atraso (`data_conclusao` \> `prazo`)  
- Detecção e exclusão de tarefas com dados inconsistentes (datas incoerentes)  
- Consolidação de todos os indicadores acima em uma estrutura de saída única e padronizada (seção 11.2)

### 2.2 Fora do Escopo

- Persistência em banco de dados (entrada e saída em memória/estrutura de dados)  
- Interface gráfica ou API HTTP (etapas futuras, fora desta entrega)  
- Autenticação, autorização ou multiusuário  
- Notificações ou alertas automáticos de atraso  
- Integração com sistemas externos de gestão de tarefas

### 2.3 Premissas

- As tarefas são fornecidas já estruturadas (não há etapa de ingestão/parsing de arquivos nesta fase)  
- O consumidor da biblioteca é responsável por fornecer os dados no formato do contrato (seção 11.1)

---

## 3\. Casos de Uso

### UC01 — Calcular métricas gerais de produtividade

| Campo | Descrição |
| :---- | :---- |
| **Ator** | Desenvolvedor / sistema consumidor da lib |
| **Pré-condição** | Lista de tarefas disponível, com campos obrigatórios preenchidos |
| **Fluxo principal** | 1\. Ator envia a lista de tarefas ao analisador. 2\. Sistema filtra tarefas com `status = 'concluída'`. 3\. Sistema calcula tempo médio de conclusão, taxa de atraso e quantidade de tarefas. 4\. Sistema retorna os indicadores gerais. |
| **Pós-condição** | Indicadores gerais retornados com valores arredondados em 2 casas decimais |

### UC02 — Calcular métricas por prioridade

| Campo | Descrição |
| :---- | :---- |
| **Ator** | Desenvolvedor / sistema consumidor da lib |
| **Pré-condição** | Lista de tarefas disponível, contendo tarefas com diferentes prioridades |
| **Fluxo principal** | 1\. Ator envia a lista de tarefas ao analisador. 2\. Sistema agrupa as tarefas concluídas por `prioridade`. 3\. Sistema calcula os indicadores para cada grupo (`baixa`, `média`, `alta`). 4\. Sistema retorna o dicionário `indicadores_por_prioridade`. |
| **Pós-condição** | Estrutura `indicadores_por_prioridade` populada, mesmo que algum grupo esteja vazio |

### UC03 — Tratar entrada inválida

| Campo | Descrição |
| :---- | :---- |
| **Ator** | Desenvolvedor / sistema consumidor da lib |
| **Pré-condição** | Lista de tarefas contém ao menos uma inconsistência (ex.: datas inválidas, campo obrigatório ausente) |
| **Fluxo principal** | 1\. Ator envia a lista de tarefas ao analisador. 2\. Sistema identifica a inconsistência. 3\. Sistema dispara uma exceção específica com mensagem clara. |
| **Fluxo alternativo** | Se a inconsistência for de data (conclusão antes do início, ou datas ausentes em tarefa concluída), a tarefa é **ignorada** em vez de gerar exceção (regra de negócio, seção 11.3) |
| **Pós-condição** | Exceção tratada e informativa, ou tarefa ignorada conforme o tipo de inconsistência |

### UC04 — Lidar com ausência de tarefas concluídas

| Campo | Descrição |
| :---- | :---- |
| **Ator** | Desenvolvedor / sistema consumidor da lib |
| **Pré-condição** | Nenhuma tarefa com `status = 'concluída'` na lista fornecida |
| **Fluxo principal** | 1\. Ator envia a lista de tarefas ao analisador. 2\. Sistema identifica ausência de tarefas concluídas. 3\. Sistema trata a divisão por zero e retorna indicadores zerados/nulos de forma consistente. |
| **Pós-condição** | Sistema não lança erro de divisão por zero |

---

## 4\. Requisitos Funcionais

| ID | Requisito |
| :---- | :---- |
| RF01 | O sistema deve calcular o tempo médio de conclusão das tarefas, em minutos |
| RF02 | O sistema deve calcular a taxa de atraso percentual das tarefas |
| RF03 | O sistema deve calcular a quantidade total de tarefas consideradas na análise |
| RF04 | O sistema deve agrupar e calcular os indicadores acima por prioridade (`baixa`, `média`, `alta`) |
| RF05 | O sistema deve considerar exclusivamente tarefas com `status = 'concluída'` para os cálculos de tempo e atraso |
| RF06 | O sistema deve ignorar tarefas com datas inconsistentes (`data_conclusao` anterior a `data_inicio`) ou, em tarefas concluídas, com `data_inicio`/`data_conclusao` ausentes (seção 11.3, regras 4 e 5\) |
| RF07 | O sistema deve disparar uma exceção da taxonomia definida (seção 11.4) ao receber entrada estruturalmente inválida |
| RF08 | O sistema deve tratar divisão por zero quando não houver tarefas concluídas |
| RF09 | O sistema deve arredondar tempos e percentuais para 2 casas decimais |
| RF10 | O sistema deve interpretar todas as datas em fuso horário UTC |
| RF11 | O sistema deve excluir totalmente tarefas com `status = 'pendente'` ou `'cancelada'` de qualquer contagem ou indicador de saída |

---

## 5\. Requisitos Não Funcionais

| ID | Requisito |
| :---- | :---- |
| RNF01 | **Manutenibilidade:** código deve seguir SRP e Clean Code, com funções pequenas e coesas |
| RNF02 | **Legibilidade:** anotações de tipo (type hints) e docstrings obrigatórias em módulos, classes e funções |
| RNF03 | **Testabilidade:** todo código gerado deve ser acompanhado de testes automatizados correspondentes (pytest) |
| RNF04 | **Compatibilidade:** o sistema deve rodar em Python 3.11 ou superior |
| RNF05 | **Robustez:** tratamento de exceções com mensagens claras e específicas para cada tipo de erro |
| RNF06 | **Rastreabilidade:** toda regra de negócio implementada deve ser rastreável a este documento de especificação |
| RNF07 | **Consistência:** ausência de código redundante ou duplicado |

---

## 6\. Stack Tecnológica

> Toda dependência utilizada no projeto deve estar listada em `requirements.txt` (seção 10). Nenhuma biblioteca fora desse arquivo é considerada autorizada — o agente de IA não deve introduzir dependências não declaradas aqui.

### 6.1 Linguagem

| Item | Especificação |
| :---- | :---- |
| Linguagem | Python |
| Versão mínima | 3.11+ (RNF04) |

### 6.2 Bibliotecas e Frameworks Autorizados

| Biblioteca | Categoria | Uso no projeto |
| :---- | :---- | :---- |
| `datetime` (stdlib) | Manipulação de data/hora | Cálculo de tempo de conclusão e verificação de atraso (UTC) |
| `dataclasses` (stdlib) | Modelagem de dados | Representação tipada da entidade `Tarefa` |
| `typing` / `enum` (stdlib) | Tipagem estática | Anotações de tipo e enums de `prioridade`/`status` |
| `logging` (stdlib) | Observabilidade | Logs estruturados exigidos pela governança (seção 9.1) |
| `pytest` | Testes automatizados | Implementação do test harness (seção 8\) |

Nenhuma dependência externa de terceiros (ex.: `pandas`, frameworks web) é necessária ou autorizada nesta etapa, dado o escopo definido na seção 2 — a solução deve ser resolvida com biblioteca padrão \+ `pytest`, mantendo o projeto enxuto (RNF07).

### 6.3 Infraestrutura

| Item | Especificação |
| :---- | :---- |
| Controle de versão | Git \+ GitHub |
| Geração de código | Assistente de IA integrado ao GitHub, orientado por este documento e por `CONTEXT_RULES.md` |
| Integração contínua | Pipeline CI/CD no GitHub Actions, responsável por rodar `pytest` a cada push/PR |
| Ambiente de execução | Local / runner do GitHub Actions — não há infraestrutura de deploy nesta etapa (fora do escopo, seção 2.2) |

---

## 7\. Fluxo do Sistema

![][image1]

## 8\. Cenários de Aceite e Teste Harness

### 8.1 Cenários Escritos

Os cenários abaixo cobrem os 4 casos de uso da seção 3 — cada UC tem pelo menos um cenário de aceite correspondente, para que nenhuma regra de negócio fique sem teste planejado.

| Cenário | Tipo | Caso de uso | Descrição |
| :---- | :---- | :---- | :---- |
| 1 | Sucesso (geral) | UC01 | Dado um conjunto de tarefas **válidas**, o sistema deve retornar as métricas corretas (tempo médio, taxa de atraso, quantidade), geral |
| 2 | Sucesso (por prioridade) | UC02 | Dado um conjunto de tarefas válidas com prioridades variadas, o sistema deve retornar `indicadores_por_prioridade` corretamente segmentado por `baixa`/`média`/`alta` |
| 3 | Erro | UC03 | Dada uma entrada **estruturalmente inválida** (campo ausente, tipo ou enum incorreto), o sistema deve disparar a exceção específica da taxonomia (seção 11.4) |
| 4 | Borda | UC04 | Dado um conjunto **sem nenhuma tarefa concluída**, o sistema deve tratar a divisão por zero e retornar indicadores consistentes, sem lançar erro |

### 8.2 Dos Cenários aos Testes Automatizados

Cada cenário acima é implementado em `tests/test_harness.py` como uma função `test_analisar_tarefas_cenario_<n>_<slug>`, consumindo as fixtures de `tests/conftest.py` (seção 14.2):

| Cenário | Fixture usada | Função de teste esperada |
| :---- | :---- | :---- |
| 1, 2 | `tarefas_validas` | `test_analisar_tarefas_cenario_1_sucesso_geral`, `test_analisar_tarefas_cenario_2_sucesso_por_prioridade` |
| 3 | `tarefas_com_entrada_invalida` | `test_analisar_tarefas_cenario_3_erro_entrada_invalida` |
| 4 | `tarefas_sem_concluidas` | `test_analisar_tarefas_cenario_4_borda_sem_concluidas` |

Cada função de teste chama `analisar_tarefas()` (seção 14.2) com a fixture correspondente e faz `assert` contra o contrato de saída (seção 11.2) ou a exceção esperada (seção 11.4) — nunca contra um valor "chutado", sempre calculado manualmente a partir das regras de negócio (seção 11.3).

### 8.3 Validação do Código Gerado por IA

O test harness existe para uma finalidade única: **garantir que o código gerado pela IA na Etapa 2 esteja correto antes de ser aceito.** Ele fecha o ciclo Cenário → Teste → Validação:

1. **Cenários escritos** (seção 8.1) traduzem as regras de negócio em exemplos concretos  
2. **Testes automatizados** (seção 8.2) tornam esses exemplos executáveis via `pytest`  
3. **Validação do código gerado** ocorre no Plano de Homologação (seção 10.1) — o código só é aprovado e commitado se **100% dos cenários acima passarem**; qualquer falha volta a etapa para o agente de IA corrigir

---

## 9\. Governança de Contexto e Regras para os Agentes

Regras rígidas fornecidas aos agentes de IA para garantir a qualidade do código gerado.

### 9.1 Diretrizes Arquiteturais (Obrigatórias)

* Python 3.11+ como versão mínima obrigatória  
* *Type hints* (anotações de tipo) em todas as funções e métodos  
* Princípio Single Responsibility (SRP) e código limpo (PEP 8\)  
* Documentação formal no padrão Google style docstrings para módulos, classes, funções e parâmetros  
* Funções pequenas, coesas e com um único propósito  
* Tratamento de exceções específico (taxonomia da seção 11.4) e com mensagens claras  
* Logs estruturados utilizando o módulo padrão `logging`  
* Código legível, manutenível, com nomes de variáveis e funções descritivos

### 9.2 Proibições Explícitas (Regras Restritivas)

* Não utilizar bibliotecas externas não autorizadas (fora da stack da seção 6\)  
* Não alterar, remover ou adaptar os cenários de teste fornecidos (seção 8\)  
* Não modificar a estrutura de pastas definida nesta especificação (seção 10\)  
* Não persistir dados em arquivos ou bancos de dados (fora do escopo, seção 2.2)  
* Não alterar a assinatura (nome e parâmetros) das funções públicas sem autorização (ex.: `analisar_tarefas`, seção 14.2)  
* Não gerar código sem testes correspondentes para as novas funcionalidades  
* Não inserir código duplicado ou sem necessidade  
* Não assumir comportamentos não especificados no contrato de negócio (seção 11\)

---

## 10\. Arquitetura do Repositório

![][image2]

> A modularização de `src/` segue diretamente RNF01 (SRP): cada módulo tem uma única responsabilidade — modelagem de dados, exceções e cálculo dos indicadores não compartilham o mesmo arquivo.

### 10.1 Plano de Homologação

Ordem obrigatória antes de qualquer commit do código gerado:

1. Execução completa dos testes automatizados (validação funcional)  
2. Revisão de conformidade com `CONTEXT_RULES.md`  
3. Análise de qualidade de código e tratamento de erros  
4. Testes manuais em casos de borda  
5. **Somente após aprovação** o código é commitado

>   
> Esse processo garante que a IA seja produtiva, mas mantém a responsabilidade final com o desenvolvedor.

---

## 11\. Contrato Executável de Interface

### 11.1 Entradas (Inputs)

| Campo | Tipo | Obrigatório | Descrição / Restrições |
| :---- | :---- | :---: | :---- |
| `id_tarefa` | `int` | Sim | Identificador único da tarefa (\> 0\) |
| `data_criacao` | `datetime` | Sim | Data/hora de criação (UTC) |
| `data_inicio` | `datetime` | Condicional | Obrigatório quando `status = 'concluída'`; ausente em outros status |
| `data_conclusao` | `datetime` | Condicional | Obrigatório quando `status = 'concluída'`; ausente em outros status |
| `prazo` | `datetime` | Sim | Data/hora limite para conclusão |
| `prioridade` | `str enum` | Sim | Valores: `baixa`, `média`, `alta` |
| `status` | `str enum` | Sim | Valores: `concluída`, `pendente`, `cancelada` |

### 11.2 Saídas (Outputs)

| Campo | Tipo | Descrição |
| :---- | :---- | :---- |
| `tempo_medio_conclusao_min` | `float` | Tempo médio de conclusão em minutos (por prioridade e geral) |
| `taxa_atraso_percentual` | `float` | Percentual de tarefas concluídas após o prazo (por prioridade e geral) |
| `quantidade_tarefas` | `int` | Total de tarefas consideradas na análise (por prioridade e geral) |
| `indicadores_por_prioridade` | `dict` | Estrutura com métricas agrupadas por prioridade (baixa, média, alta) |

### 11.3 Regras de Negócio e Restrições

1. Considerar **apenas** tarefas com `status = 'concluída'` para cálculo de tempo e atraso.  
2. `tempo_conclusao = data_conclusao − data_inicio` (em minutos).  
3. Tarefa em **atraso** quando `data_conclusao > prazo`.  
4. **Ignorar** tarefas com datas inconsistentes (ex.: conclusão antes do início).  
5. **Ignorar** tarefas com `status = 'concluída'` que não possuam `data_inicio` e/ou `data_conclusao` preenchidas — tratamento idêntico ao item 4, sem gerar exceção.  
6. Divisão por zero deve ser **tratada** quando não houver tarefas concluídas.  
7. Fuso horário sempre **UTC**.  
8. Arredondamento: **2 casas decimais** para tempos e percentuais.  
9. Tarefas com `status = 'pendente'` ou `'cancelada'` são **totalmente excluídas** da análise — não entram em `quantidade_tarefas`, nem em nenhum contador ou indicador de saída, geral ou por prioridade.

### 11.4 Exceções

Taxonomia mínima de exceções que o código gerado deve implementar, cada uma com mensagem clara indicando o campo/tarefa afetada (RNF05). Inconsistências de data (regras 4 e 5 acima) **não** geram exceção — são silenciosamente ignoradas; exceções são reservadas para entrada estruturalmente inválida.

| Exceção | Quando disparar |
| :---- | :---- |
| `CampoObrigatorioAusenteError` | Campo obrigatório (`id_tarefa`, `data_criacao`, `prazo`, `prioridade`, `status`) ausente ou nulo |
| `TipoDadoInvalidoError` | Campo com tipo incompatível com o contrato (ex.: `id_tarefa` não numérico) |
| `ValorEnumInvalidoError` | `prioridade` ou `status` fora dos valores permitidos (seção 11.1) |
| `IdentificadorInvalidoError` | `id_tarefa` ≤ 0 |

---

## 12\. Considerações Finais

### 12.1 Ciclo de Vida do SDD Aplicado a este Projeto

1. **Especificar** — este documento, escrito antes de qualquer código (você está aqui, Etapa 1\)  
2. **Gerar** — assistente de IA produz o código em `src/` a partir do contrato (seção 11\) e das regras de governança (seção 9\)  
3. **Testar** — test harness (`tests/`, seção 8\) valida o código gerado contra os cenários de aceite  
4. **Homologar** — checklist da seção 10.1 confere conformidade antes do commit  
5. **Commitar** — só após aprovação explícita (nunca automático)

### 12.2 Pilares do SDD Seguidos

- **Spec-first**: nenhuma linha de código é gerada antes da especificação estar completa e aprovada  
- **Execução determinística a partir do contrato**: dado o mesmo input, o código gerado deve sempre produzir o mesmo output — sem ambiguidade de interpretação (é por isso que a seção 11 existe)  
- **Testes derivados da spec**: os testes (seção 8\) nascem dos cenários de aceite, não são escritos depois "para cobrir o que já foi feito"  
- **Governança de contexto**: o agente de IA opera sob restrições explícitas (seção 9), não sob liberdade criativa  
- **Responsabilidade humana**: a IA gera, mas a homologação (seção 10.1) e o commit final são sempre decisão do desenvolvedor

---

## 13\. Glossário

| Termo | Definição |
| :---- | :---- |
| **SDD (Spec-Driven Development)** | Metodologia em que a especificação escrita é a fonte de verdade e o código é derivado dela, não o contrário |
| **AI Harness** | Conjunto de regras, contratos e restrições (seções 6 e 9\) que "encaixotam" o assistente de IA para gerar código dentro de limites previsíveis |
| **Contrato Executável** | A especificação de inputs/outputs/regras (seção 11\) tratada como interface rígida — qualquer código gerado deve satisfazê-la literalmente |
| **Test Harness** | Estrutura de testes automatizados (`tests/`) que transforma os cenários de aceite (seção 8\) em verificação executável do código |
| **Homologação** | Etapa manual de revisão (seção 10.1) entre o código gerado pela IA e o commit definitivo no repositório |

---

## 14\. Arquivos-Guia para a Geração de Código (Etapa 2\)

### 14.1 Arquivos Vitais

Nem todo item da árvore da seção 10 tem o mesmo peso para orientar o agente de IA. Os arquivos abaixo são **vitais** porque são a entrada direta que a IA vai ler e/ou o esqueleto que ela vai preencher — sem eles, a geração fica sem trilhos.

| Arquivo | Por que é vital |
| :---- | :---- |
| `specs/task_analyser_spec.md` | Fonte de verdade — este próprio documento. Sem ele não há contrato a seguir. |
| `CONTEXT_RULES.md` | Traduz as seções 6, 9, 10.1 e 11.4 em regras diretamente consultáveis pelo agente durante a geração — hoje é só referenciado, nunca definido. |
| `requirements.txt` | Fixa as versões exatas das dependências autorizadas (seção 6.2), impedindo que a IA instale algo fora da stack. |
| `src/models.py` | Define os contratos de dados (`Tarefa`, enums de `prioridade`/`status`) — todo o resto do código depende dele, então precisa existir **antes** da lógica de negócio. |
| `src/exceptions.py` | Define a taxonomia de exceções (seção 11.4) antes da lógica de negócio ser escrita, para que `analyzer.py` já nasça lançando os erros certos. |
| `src/analyzer.py` | Assinatura da função pública com docstring completa, mas **sem implementação** — é o que a IA de fato preenche. |
| `tests/conftest.py` | Fixtures de tarefas de exemplo cobrindo os cenários de aceite (seção 8\) e casos de uso (seção 3\) — orienta o que "sucesso" e "erro" significam em dados concretos. |

`.github/workflows/ci.yml`, `README.md` e `.gitignore` ficam fora dessa lista: são importantes para o repositório funcionar, mas não orientam *o que* a IA deve gerar — só *como* validar e documentar o que já foi gerado.

### 14.2 Estrutura Padrão de Cada Arquivo

**`CONTEXT_RULES.md`**

**`# Regras de Contexto — SDD Task Analyser`**   
**`## Diretrizes Obrigatórias`**   
**`(copiar seção 9.1 da spec)`** 

**`## Restrições`**   
**`(copiar seção 9.2 da spec)`** 

**`## Stack Autorizada`**   
**`(copiar seção 6.2 da spec — nenhuma lib fora desta lista)`** 

**`## Taxonomia de Exceções`**   
**`(copiar seção 11.4 da spec)`** 

**`## Checklist de Homologação`**   
**`(copiar seção 10.1 da spec)`** 

**`requirements.txt`**  
**`pytest==8.3.3`**

**`src/models.py`**

**`"""Modelos de dados de entrada do Task Analyser (contrato: spec seção 11.1)."""`**

**`from dataclasses import dataclass`**  
**`from datetime import datetime`**  
**`from enum import Enum`**

**`class Prioridade(str, Enum):`**  
    **`BAIXA = "baixa"`**  
    **`MEDIA = "média"`**  
    **`ALTA = "alta"`**

**`class Status(str, Enum):`**  
    **`CONCLUIDA = "concluída"`**  
    **`PENDENTE = "pendente"`**  
    **`CANCELADA = "cancelada"`**

**`@dataclass`**  
**`class Tarefa:`**  
    **`"""Representa uma tarefa de entrada, conforme contrato (spec seção 11.1)."""`**  
    **`id_tarefa: int`**  
    **`data_criacao: datetime`**  
    **`prazo: datetime`**  
    **`prioridade: Prioridade`**  
    **`status: Status`**  
    **`data_inicio: datetime | None = None`**  
    **`data_conclusao: datetime | None = None`**

**`src/exceptions.py`**

**`"""Taxonomia de exceções do Task Analyser (contrato: spec seção 11.4)."""`**

**`class TarefaInvalidaError(Exception):`**  
    **`"""Exceção base para entrada estruturalmente inválida."""`**

**`class CampoObrigatorioAusenteError(TarefaInvalidaError):`**  
    **`"""Campo obrigatório ausente ou nulo."""`**

**`class TipoDadoInvalidoError(TarefaInvalidaError):`**  
    **`"""Campo com tipo incompatível com o contrato."""`**

**`class ValorEnumInvalidoError(TarefaInvalidaError):`**  
    **`"""Valor de prioridade ou status fora do enum permitido."""`**

**`class IdentificadorInvalidoError(TarefaInvalidaError):`**  
    **`"""id_tarefa menor ou igual a zero."""`**

**`src/analyzer.py`**

**`"""Cálculo dos indicadores de produtividade (contrato: spec seção 11)."""`**

**`from src.models import Tarefa`**

**`def analisar_tarefas(tarefas: list[Tarefa]) -> dict:`**

    **`"""Calcula tempo médio de conclusão, taxa de atraso e quantidade de`**

    **`tarefas, geral e por prioridade, seguindo as regras de negócio da`**

    **`spec (seção 11.3).`**

    **`Args:`**

        **`tarefas: lista de tarefas a analisar.`**

    **`Returns:`**

        **`dict conforme contrato de saída (spec seção 11.2).`**

    **`Raises:`**

        **`CampoObrigatorioAusenteError, TipoDadoInvalidoError,`**

        **`ValorEnumInvalidoError, IdentificadorInvalidoError: ver spec seção 11.4.`**

    **`"""`**

    **`raise NotImplementedError  # implementação gerada na Etapa 2`**

**`tests/conftest.py`**

**`"""Fixtures de tarefas de exemplo — cobrem os cenários da spec seção 8.1."""`**

**`import pytest`**

**`@pytest.fixture`**

**`def tarefas_validas():`**

    **`"""Tarefas válidas com prioridades variadas (Cenários 1 e 2 — UC01/UC02)."""`**

    **`raise NotImplementedError`**

**`@pytest.fixture`**

**`def tarefas_com_entrada_invalida():`**

    **`"""Tarefa com campo estruturalmente inválido (Cenário 3 — UC03)."""`**

    **`raise NotImplementedError`**

**`@pytest.fixture`**

**`def tarefas_sem_concluidas():`**

    **`"""Nenhuma tarefa concluída, para testar divisão por zero (Cenário 4 — UC04)."""`**

    **`raise NotImplementedError`**

---

Nenhum desses esqueletos contém lógica de negócio — só assinaturas, tipos e docstrings apontando para a regra da spec que o implementa. Isso mantém a Etapa 1 dentro do próprio escopo (seção 2.2: sem código de produção) e ainda assim entrega trilhos concretos para a Etapa 2\.  


[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAi4AAAHfCAYAAAB3bFP+AABt8UlEQVR4Xuzdf0wb198n+v2b//JnpMqK9FXU0KBaRQIVgfKDSFhIsVAVQG0gakSS5rdk0W5I0IWnTUBdgtBjetk1m+8NPGzpOnlo4CYlJCGBe+GuJWvre61rEhTC9YKABNaQsMZbPY//+tzzOcPYHo8BEyYEw/uPlwozZ2bODJXOO+ecmfNvgn+FCQAAACAV/Jv4DQAAAABbFYILAAAApAwEFwAAAEgZCC4AAACQMhBcAAAAIGUguAAAAEDKQHABAACAlIHgAgAAACkDwQUAAABSBoILAAAApAwEFwAAAEgZCC4AAACQMhBcAAAAIGUguAAAAEDKQHABAACAlIHgAgAAACkDwQUAAABSBoILAAAApAwEFwAAAEgZCC4AAACQMhBcAAAAIGUguAAAAEDKQHABAACAlIHgAgAAACkDwQUAAABSBoILAAAApAwEFwAAAEgZCC4AAACQMhBcYFuafif++y6k2w4AAKktJYKLZzJE02NjFFxK3BAFuMzoAgUmJ3T7toLAUphGxhYoOPtGtw+Mx/8/FNh9ZP0ijwKeTt1+AABIXVs+uHAjdMA+Rrt3m2n89yu6/WxEBIPdZV1U8DczBXxbq6Hi+mc3+WgP178ncf23kuvuEKV9Ukppor6s/DMzBf2PdeW2sm5/mNKyaqjyoKj7jEu3HwAAUteODy6VfW9oX1Y5eW5dEL8n7tHZiFQLLgOTIrzYu+j0T3ZK++xUygUX2dvi4P9fssjT9mH+pgAA8PF8tODCcxDGRycouLSg28d4eMUz+obG/RMiuPgSBhc+h8c3QZ7JN+8dXIrvTNCu3XnkcZyilRo5WRffG5r2j61Yho34QxSY0Q5XGR1ckq0LX3dEPL+VhqfG58V5vBO6+qo8Yn+atY2KDQgu47PibzWW+Doqj39h+Z70+2LJ+1pl2O2hCF5peXVUmYfeFgCA7WjTgwv/i/6ArZPSPsmXQxH79pjp+uVTNO2LNo7tvhDtKqiLDFew2ODCjde1P95Q2mflmjLrCS4N3hCl7dEez6x8jtEuWcYlGtzs79pEOaWucuhENIjT7ug1ZF16Jmj3wQuRMsX5eTTQdpOC797EBZcaeYyDr/2FjfaJbZ4OvqeVA4gqmbqU97wRISyfTp8X95V1Spbh67ocNrFfCYgO8Wz3WWvEvqzIea6X5VNwUtvIrxZcyn8Xz15c52FVYSR4cvldX7XRAfH3DHja5LZ2zwLtK+G/o3KtA1+Yqb1e3O+ML3KubhH29nxtjz67L7NofKBV7lOfHW/nZ9XeUUO7v7oZua/pPuV5qri89dbYmkEUAABS16YGl+mlMO37YVBpoArz6VptHRVX2cmcVUrjf9TJMgOigd5VqDRk5SWFdKCCG9k8TXCxe0TD/+kp2XidriinfV9dkeXXE1wGZkTgsD+gfWVKQDpdkk/X6+3UfUs0mvNK78C4qG9x7WOqtF2hyp9EPb/m62SR/essEUrGlLpwCPnbKTKLBrvy8gWqFOfYV1JDDV+LRn3ep+txcXgXRKi4In/3tCUXWpKtCwcXDhT8rCq/K6XyWvEc/1ZKp0VgCE4OyjIPxX0Xf9dK16pr6HS1nXbnK4HL1VCqqctqwcXJc0i+uEIXY3o17D7lOTR8JeozPyb/jmn5dlmX02WldK3+Jh04f1OErUIRDB/IY/hvsMvaKoKG8rc2lyj3FDs3xTH0hswV0WCz5xPx389EWQ4uQ3ZNvfje0g7epItfRu8XAAC2l00NLiPvREP1dZf817Prt5rIv9YD/OrqcpnTy41v9w/8r/loj4UaXKbF7+Zal/x95DfuSVDP27mu4KJKZqhI5eLGvKCVymOCQOWACCK7C+l6SR4FxmJ6LZZfxY2t//UmG6V9qYYWrvvq11tNorqoweVhdZF8turzXu25cA8MBw5HmQgcS9HhnNWCC4eofZcHlfAwcDOmpyMr8hydPGTz+RUqFvUbd/G1l+815m9d/NuEDKUPa5X6ymBbNSj//+DzquVOc++auC/rp+Jcnk45dHhgT1akZyf2fPJv2bL23xIAAFLTpgYXbuDKZWOlDHdki0bRXmujaZ/S8KqNPP8L3HNLaXx4W+zkXLUxzha/B9zKkEL85FwON8UtPjLnl5L5YFFEtuA4Xy57BNQ6rRVc2t0LVPCdnXZ9XhT5V39sYy57DZZ7iLjep0sKaeBOqxwmir2nSI+B4LqlDS0cEg5c7tLUVdY3v4gG7NFhnrXqogYXV5PSeyKfy7cPNMGFw0FDzxiZS2pEYIkOO9m5p+RdcsGFXezjaxXK0DEyv0C74wIShxvzcu8asx7MImdLXWSYSIaUapfy/0FWFh0oLJfSvihSQmmHEkqZGlyc5/NlmPX4Q+RxeSLPmMkengI7nc7i+qK3BQBgu9rU4KJyet5QcVUbpX2mvHab/Yn4F/YT5V/u5nrPcsPFb4QoDX9scPFwcPlK/Kv7k+hcioTBxe6hfXmltO/LwgizYP+uNOngct21IBr3cjKL857+7hSdrr1JaZ+f0jXmI6KRv9bhigxZMce3eXIIJz64sOscEmY8keM5JGSf7xJ1LNLUNztPhKAmfg4LSdVlreCi9oxwL8cB0cBX2mxk/YHnjBSuO7jIYZkv6+SwjsMlAsinFzTDVozDib1vjA58x9dQQtJpHsYR55PBxaYEm+wv8yLBhVm/KqfxvugwkBpc4oezYvG8G57f47KXr1gGAABS30cJLipuSAtauFHPksMbAdFA86us/PtAvdJIxQcX/pf87ooHynBCnzIvJj64xF9nNZHg0qJt8DS9P8uhZq3GnHXzEMmXNZFJvrFzXAbuXKF9lx8owaYiXxOgVpNsXdYKLrG9VdPLvVXtY2EldKwzuHDwMFe75N/hwHmbfP14ZJXXj/na/HdT5/rIv+vyEJoaUleyVnDhYTOeK6P0tujrCgAA28emBhe1Z8FhK6XAjI+6fQu071tlcqY6L0HOufjsAhWIBtPT10rXe0Sw+fyCZnLu6eW3WioLs8jjeUzlLTzkUPheweXaEM9RKaJrJXn08Mljcva5aNqnzFWxdvCw1nKoerdA1/rE75+Wa65zbWCBrPmnaORJK43Ph+hih0eZEMuN6OSgJrhwg81vB+0p65ThxflDkSYsrCaZuqwVXDj07bn8WNZlhEPguxAVt3jkMdcKRH1no71AyrFdZP7ETA876uRzGXdpQ4Eyv0cZtir+VAlq6j7+CFx2YR0NOGw0Pf+G7AOivnlXlHkxLqU3pX2U3666QqcPimv0ddHDAQ+dtj8gZ7Ut8lxc/hBZm7hnJo8c5wvJ4xrUDBExnhcle1ua0NsCALDdbWpw4Veh95W1yoYuFg8fBMaUN01kL4xd6YWJLRMbXHi4iBvV+PO8T3Dhc+2p0J6r/bt82XDKb4LkK6/fRurxuVIvfhU4sLRAF++MiQAR/dIs4yA20HRKTjiNDy58TT4vz4vhcg/ry1f8lk2sterC51gruPB51CGn2LqmfZan1C/uOzn8cb7Yr+iqbwyp++W8koNKndor8jSTe+3uBdp1MDp0prJ/q+1puih7Uwo1ZSrzOfS5lGfXoB1m4wm6sQFJvoZd0qZMUh5DbwsAwHa3qcFFxWsP2e+4qKGplVx/iEZoXvsvaDk34ncfXW9oFf/abyPP2Bi5XD4KzoxFzyEazeu3BmUZ1x+d5Bqd0E3YTBZfr31gjOyOTvI8eaAJEvyhNkePR9RV1KOvS/Z2dLsmRBCIvkHEx/O26y1d1O5ojfTYqLjXwDUk6jYbbdhHRP0HhnzrqvNadRmZUc4ZiPmQm8u3oLuGSzz/ho5BsttbadzzWPa8dPeJ5zsbPU41IOpub3tMD3/voumx6PdXZH14nspyD0586GEcPAbE9RvE8XytEe6xSRDSnO43dF3cU0ODnVzivjR1FdcfEM9OFX8vF58ob3UpQ4v6cwMAwPbyUYILpD4OJNZ6nq+Tpxtm2kwOlwg9P9zEm0QAADsEggusmzoExUM3p635mq/3AgAAfEgILvBePL6FFdc5AgAA+FBSNri8mpyV4rcDAADA9pWywcX3cpL+072nuu0AAACwfSG4AAWWxH/n8UYOAABsfQguBuFXjB0dj2na835vt0zPh2l8dCLh68LJ4tePR/wLFJhc39wT/pDcvk+LaOQ3fqUZH3ADAICtC8HFALEfSrN/Zdas15MMudJzYSuVf84fXnv/j6jFf4Aufn8i8lP833bRgT3myKKVAAAAWxWCi0HsngWyfl1Dnt94/SR9aOCv0O7LKifPLf16Ph8zuFzjL+l+UkrOy8rKy/H7AQAAthIElyRwj4rL94YeDnnI0eOi07Vt5LqVOKCsZLVVqOODy/js8rDROs7PYoPL9LvQmkNPcu2i7x7I3hZ10UUAAICtDMFlFfwp/4sdPkr7LLq2j+p6oQgZ8z6lx2J5oUG5zk6e2D4T/eR/gzdEaXv0x6urR3MZNbjwgobZ314g/hqtPFdBVuSLsA5ekPBvF8jxtbKKc/yq2VxGDS4FheL4z5Q1hqwiDI0PJA4l190Lsm5ybSb0tgAAQApAcFkFrzrMQaBYhBHHLTuZv2ulPZ9k0cN6ZQFFLvPQH6LrTV1UXmuXq0LHB5eBmTBdsz+gfWV1MkicLsmn6/V26r4lwsT88grIy8FFBo0sM12srqPd+Tb5u8eurHi8nuDCCyeWf11EBypqZAiSK1X7tUNQ6jpD2SIsTQ8pqzUDAABsdQguK+Deln0/DNI+EQKmn/CwkAgpIoSkfVlHF7/kcKJ9e0juy7upCy6qZIaK5MrHPqUXpnJI6clRV35eT3Dp/oGPeaPcQ5VLlhn5zaa5pp17gv52SlnV+d363kICAAD4WFI6uPzHzl76/6bm1hR/bDKmhex6j9Lod/CE2jC1j4mA8blteVFB7UrJRgSX2Mm56hCUEkLWF1xiJ+da2ybEtixyydWTlW1KoBlEbwsAAKSclA4u//j336n11z/WFH9sshw+ERa+sNEeEQ6yC4pEaCmSPTCJvneyVYNLcQcHlzwa+Kkoss3O9/WpONe36G0BAIDUktLBxYihIs9smE43PKaGH65QYCzR8E8d7fvUTFZrKTVUX6Fxd+LXlZMOLi3KnJXYfR8quMjvy9R75JwXNTBxb4u52iUnAk8P3NTVEwAAYCvb0cGFG3Z1KIUnwjrPa9+uafAobwQVZJnpWm0NNTTZqftOpwg40WGiERF8BoZ81PCHSw4jFX9hpod/tJHH5REBI3qua8tzVq6V5NHDJ4/J2eeiaZ8ScJIJLk4/D1NdoYsiGI2LgFX5G7/tdCphcOG3kaZFmYaBCVkmdu6MDECfiQBUxr0tY7pnAgAAsJXt6ODCTv+hNPYcXJThlOh3T8bfhSm7+nEk2Kh4bsj4E6W34mIfBwzl+JVed2Yeca49FV2aMvI15HcTSQUXfgsou3pQe52/ZSUMLrFleGjL1XZFnkOdtxM74RgAACCV7PjgwkMn9j/G6GFbW+T1ZMZBoaHDI7a3RnpOxkXAKL7lkeGg26b0zqg9LgNDHo34Hhf1Wu0DY2R3dJLnyYPIK9Xc8zPgfUMetyeybURca8Dlo+nRaO8OL4boHJogZ1uX2O4R1w6RS5QJzowpx8yE5e8u3xg57rhEuU4K+D2R4508ufiLK2QvyRL3qhwDAACQSnZ8cFmJXMOnrIsKPjXTw99bZRjpHvCQ+Xyn7MkYqNf2zqQC/ubMxepOmh5o0+0DAABIBQguq7j25E3ir+aW5VNwMtqTAQAAAJsDwWUNPLwz4JmIDAHFDt0AAADA5kJwAQAAgJSB4GKAjq5+3TYAAAAwHoKLAW7Yf9Vtg48rMKv9yB8AAGwPCC4GSKXgMv0uTCOjbyj4Lrk3ovgVcI93ggKTqbM0AH+sb/eXNdRdVar5oCAAAKQ+BBcDpEpw4Ve8d33dpXxJN+bjeInwpOTiWz7NB+0qv8qnh//PoFwGIfYDd1vpY3b8TZyCFh/t3p1FnjZeHBM9LwAA2wmCiwG2Y3Bp8CrLHZwuyCLnnTa62NRF3fU1NDL/hq7fclFlvZ12FVzZcsGlezJMaV/WUeXBxGtGAQBAakNwMcBmBhfuUfCMLSQ1dMNlR0TZ4KwyXLKe4FL+Oy8fkEcuu35RSMbLB5hr114+gHtuPL6JSB3e1/isONfY6vcs1566xQtPZpHnFnpbAAC2IwQXA2wkuFx8wmsSFdLDKmVNokT7XPXKas8OzwLtyq+JDNM0fCuOmVR6FeRK0E08tKMM37R31NDur27K3/dwuOir0QUXPub0HV5ksoisn4ky7jY5p+Why0cF9coaTQ5bEQ0MDOqWMFgruPC5K38X5/5U+YAf16H7p1NybSZ1wcjrBWYKzmu/i6Pss5H9K14Fe4zaxT3vK+GhKWW9qANfiHurv0LBGf33dNQVunkhyuCkdqVvAADYHhBcDLCR4CJXa/6UV2vOooFJ0dDn22UYGBdhwNqm9B7wIopynaEva2QAOP1tKe376opsyO28yvPyukOOoTdkrrBHgs2eT8R/PyskM4eLIbsmuEyL4HKxR1zvkyIq4NDiUpYBuO4W9fmkNHIOVbEoE/Q/iNR7reBSyaFLnMcsrlV+/gLtyhNE2YGGcnLNLSiLSooQMu4fpH02ZfFIV0MpNbjfyCEqDnIDMwvyefBCkqfLSula/U06cP4mlecViuAVrQuTvS0dE+IaeeRxiICE3hYAgG0JwcUAGwkuA7MikBy8SdfyRQhxuSjtb6eUBr7llAgGLrkS9bS7lQ7YfXK7OgTCi0DuufxYCSUDykrVTF3tmsPJuKdTHndgTxYFPG2R4FLwNzNdtNtlsOC1mNTQwlbqcRmJWQCSrRZc1HWe1LrzNtkbIu5ThpVXj0XdB2U9BsS10wpaZXBxfJtHp3/3iPvMF/d5ipyTIdkzU8zHuDrlfctrvFvhOYqQc/pL9LYAAGxnCC4G+Iemf6Jn/8WblMXQv2iOHREBZPe3D6j4czOdvsULOCpv8TR8ly+2t1H558sN/fnHSkhYDincw3DAPrYcZqI9DGpwcZ5XVq/2+EORYR41uKi9KDK0DCnBIt5G5rioQzZc9+DkY7lN3mdMmCloGRPHZlFDWw2lfXZB1oeHeArqO+V2vk8OZ+YflN4YZj2YRc6WuoTDROV3uLcln1wt6G0BANjOEFwMwMHl9A+NSYkPLnJuSr2HzKJBN39rU4Z3vigi65fiv3kX6HphFo3P+Wh3xQOld8VljxxX4BiTvSKelmi4UIMLD7vEN+DxwYV11yb+1slGgks3B5esGjqdFe394BASew88f2fX7kKyVpTLwLE7r5Cy/2amPSU2zeRhntxr7xujA9/xfB0l1MleFb8SiJhrVtxXYatyvZjtAACw/SC4GICDy8v/9jop8cGFqSFBNsp5Ztp3WRk6Yc7L+TS9+Ib2VbnkXA+e78LHyOBQvbztjrKNJRNcOBg4BzopLf+mPH7Afko3MXgjwcU1H5bDPzwUFPDxEM/ytsLoNrsvJIfF+B6z95ipuD4aTOSrzLP61bflEJQIPzzPZ7wn5p5FXWVvywp1BQCA7QPBxQAbmePCYifEOiryyHrLFQkyamN8sY+DRCFdzBeNtvcxXe8bo7RPT2nmdLj8IbI28dBKHjnOF5LHNah5Eyj+raJ2nhicdUUGAU8HB4Foo79WcJFDVS3KUFX7T+XU/cRFrp7HMgBxqOFeJHk/oh4jYz4qbuHf86ld3B+/WaQOJ8mwlmUW9/NYTsqVx/CE46UJ6vaL8xTW0YDDRtPzb8g+MCGOuaLpeeJAtOurNjl3Br0tAADbH4KLATYaXORH075QXnN2NZXStSEODUVKz8IfNbIMD7Vk10bnezDu7Ri5w/tDypBTg/I6tCr+ey3xwYW3NbgXKO2zUzIMjPdEe07WCi7MORaSbzqp1+M3j9TzDohgsvuraM+RrM/nYr9H6YFR57zIoPJ1FnWPjcnhJf594KciUWaB7KJuuw4qb0/Fsn+bH3mTSg10/LYSHxNfRwAA2F4QXAyw0eASEI34gOcNuYY8FJgZo3ERMAZcY+TiSbXzMd9O4fkef4zR9YZWsjfZadyt7WHgHpcBcQ5V/LdXONwM+N7otrvGlOPGPfzmkBJSPCJ4DAz5KOAf09U31sisqNMdFzk7OsXx/E2ZaMgZmRfBqMMl69ve0irOpR3+cY0uyOtOj/oiz4B/D0xGr6nUeYEa2h6T3d5KIy6lV0fWkYeOvu6UE5uDY9rXowEAYHtCcDHARoMLvB8ORhftg+S6xW9aobcFAGAnQHAxAIILAADA5kBwMQCCCwAAwOZAcDHAVgou75b+RYrfDgAAsB0guBhgKwWXhv9wh+YX/6duOwAAwHaA4GIABBcAAIDNgeBigJ0cXPyvQxRcfKvbDgAA8CEguBhgpwaXX8bDZEo/ScM3rLp9myXnhptyjhRLNULwL7euDAAAbB8ILgbYqcFlRuh99IqCr5/r9m0W/1yI/FOzVOGcpXPpuWLbsK4MAABsHwguBtipwWUrOfcojOACALADILgYYDsGl1bXW8oprZVDMOdKi2nGdTeyzy/YmobJVl0vuTvrdcev5d5EmOqqmyk4pQ0ato7nNHq/WV6jTlyj9ekzyjlaSTWiDvd8blGnevlzcE47JITgAgCwMyC4GGC7BZdzj97SoQwrebvr5TBM3aNX1HujVuyLTsLlSbm879BNL/V+z4FBf57VeAVT0W3yd1yKbOtfCtP+7EYKDjZG9jceyyXvlJdM3/xKdeLn0ZduMp26S6OOk5rzIbgAAOwMCC4G2E7BxS2YChzkbzuj25eIpeXVewUX9djWE3zsrPy9akjItlBwyR0JLsFHHJjEz98Pk7dFCSuxP6sQXAAAdgYEFwNsteASeBei//E//zUp8cfzm0KH0kUo8N3W7UtkI8GldSJMJekiIE0pw1D7f3RT/48W+TOCCwAAJILgYoCtFFz+3b93yvrUNXeuae7tku74xhcijHBwefHhgwvPYzF9c1cOF/WLn3N4mOjPZrkPwQUAABJBcDHAVgouGx0q6l0SwSCjNhIY1rJWcHG/Fh6JMLGU+CN11rZZcp7Npbo/Q1Qnv8OivFqN4AIAAIkguBhgOwUXlvmjm2qKRAh47ZW/e+eFp4kDwWrBZVQwHfuVTCJQrPSRutapMJWlX6KcmkZyN3FwUbavN7jU/cnn4beNepRtS/prAQBA6kNwMcB2Cy5e0ejnnL0rAsdh2pttof0ZudRbzUFBmUSrhgoOJLEaOez89SpyHjkUdLJH7vPGvQWkCnCZs32Uw70lXke0DsvXSDa48MfwMquGZV335lip/RTXJXEvDwAApC4EFwNst+CimlkUpkRYWQrp9iWLg0ng9eoBoqI7RK3fcNBQgtFG8Jd0A683fh4AANiaEFwMsF2Dy2ZofxGizLyrFHi6/o/YAQDAzoPgYgAEl/eT0/ScLNm5NHofoQUAAJKD4GIABBcAAIDNgeBiAAQXAACAzZGywaV/+P+m1s4/dNs/hv/T7dNt+1i4LgguAACwXaVscNlKPS4AAACwORBcAAAAIGUguMCaeoWcnHoKDirrCAEAAHwsOzq48BdYY7/8eig7l4ZbKin2i6vxZViiNXGqhkTZdAs5L/C+6Afb4r8yu1ewlVoo8LIvUoaDgSm9luqO8LHKWj28SrMp/aTma7S8Hk98XViy6wq9L7V+H/o6AAAAa9nxwSV2nZ1fXoTIlHFJrla8UpmV7P/RTRUXiqki4yQF56OhRA0u6ifq/YthKmlxkyXDSkGfsgLzPV7YUAQDS4a4zrjyhlJZV4j2Z1t0wSVRaPrQEFwAAGCrQHCJCyXx2+J/T6RfyMluJO+fzTKkBLqvRvbFBxcm1+e50BfpnWl8wQsEniTT2UoKdHGPjxKEysTvjUeNCy5uobW6h2qeDlPOkTPUfvY4Nbq9lHO0klrFz8Gl6DpDtvuTsoz1SDHVddaK4HIVwQUAAD46BJeYUCIXBfzmLvX/aFmxTCI8TFSVzce4Kefn55ryiYIL4x4VG/ewiBDCweWcCC4lHcq1+RiLOMbW9qsmqGw0uKg9J87vrXRvapJM2fXUfsFK/VOvyHSkkYLLn923PQ3JHqHRoWYanZoly8/uTRmSAgAAWMuODy413+TSvfvPqF04dPk2ncsTDfRcNBhwmZKCXLJV10cEvT2a83BYUcNO3Z8iXGQUU3BJOcdKwSU2hPAxddyz8edzajxaTM75V+L3ShFonstAExtceBVlW/WlSF3cncl/Lp+Di4WHfF7c1qy+HPuzDG8n7pL752LNcRgqAgCArSClg8v/2t5D3tH/tqb4Y1VqKCkRAcCUXkz9N85QcHFSV0YNN6rghDeyn4df9h9ppuBgo/ydh41M2Y2RRj6Z4MI/81yW/r9eUYk4tqr7LvV+b430xASXnkWOsaZzXZojdfG7lX3JSCa4yJCSUa8JKQguAACwVaR0cPnHv/9Ov/UMrCn+WFXsMJCl+RXViRATXFLe6klUJhHuLckRocf2vdILco5D0MFLkWNWCi4lHbNUlc1l3JHgEhDBxXS2jw4VnZQThDm4WDi4vFAm8RoxVJRUcIkLKYm2AQAAfAwpHVyMGCpSA4ab3+wpaCZvszZgrBVceJio7oS2R6bk5jM6x/NXloYTBpfIXJoaZXiJ57v8coyvMSkDzSEOJ77bmqDB5ZINLjz5997QJAVeujXbkwku3INkOtKsebMKwQUAALYKBJeYUMKTbC3p0deUE5WJpTbysW8RsV4RgvZn1Mrho/jg4p0P06GqPuXV5xfKq8+WlleRa8wsClOzxG8byQ+/cWD4U/nwW7LBxfaUg0YulfA1pqLzcZIJLlwu84aX6vg17EWl9+nc/bfifFYEFwAA+OgQXGJCCfdUZFYNK99OWX41mMvEf/DNwuFBNP513jBV8ETcmO+2xJ6be1TUUKAem2nOpUZ+9fh1dJ5MbHCJFT/fZKUP0MUPQ9W4uJyVbDzReD4acpINLsNzYdpb6pB1zcwpptYbx8X+ZgQXAAD46HZ0cNnOZubFfxejXwB+H/7XIRF8NnYOAAAAIyG4AAAAQMpAcAEAAICUgeACAAAAKQPBBQAAAFJGygYXl2eU/v6f9W/zAAAAwPaVssEFPS4AAAA7D4ILAAAApAwEl7+UD8/5p94Kswm/faLuD7zmL9rqj4cPzz8XUv4+m/hdmczqYeq/EV0lGwAAPr4dH1xqnr4lU/ZJyszOpf0Hi2l/Ri711vCXaJWQUucW+81nKCfnsChnJduRwxR8HV2Rmb96G//1WnXRxOBfryL7E5Ff4B1XPvvPCyqa0k/qyqjnbR3nZQQuUSDm67Xq+kqjbZci6wnFH6/qrdJ/mXcl8XXmL+jeqz5DwSVl5ez4xR9V/LXg2OfA51GfQ/w1WPxXhVWxx/TzV3yPNsu/S+YRq9h/mGxFFvHckl8V+33Ff1kZAAA+vh0dXHhtokMZVpp52hjZNvw6TDNu5TP5TtFoZmZU0sx9JSzMCJYbXk3Dyo3zoaNWqivgBROX1/aJCS6x11ttraGVwkAsi0O7gjUvyBi7PIEqfn2k9YoPHL0TIRGQGqn/R6v8faW6vm9wWamecjHKkz3ktIlnu6T0tMyIsNbY4qXgnP4ZGg3BBQBg69mxwUVdodndtPJQQKKG1zkfpv3plRQcUsIOl6kTjdv+AodcVJG3fajgElnB2nFShqocEarUBRhjrRUI1pLovmO3rVRXo4PLMO/PE/e3HBzfB/+d65qGqfXpM8o5Wkk1pcV0z+emnNJ6+XNwLrqC9r3xsNyec6SY2m1nyHTZgeACALDF7Njg0joVpkPplzQrQccz2Z5R/4/ckxLdpja2ow6lsVUXSLS2zZLzAjdyoQ8WXBj3EpVlWCnz+/pID0i8tQLBWhIFjv01bmo9wdtmV6yr0cGFZf7oppK8XPIP8bVCuv1rUa/ReCyXvFNeEVZ/pTrx8+hLN5lO3Y38HXvnOSSJZ/rzSfJPTVLd0CSZMk4iuAAAbDE7Nris1PiqVmpUeaKu6WxfJNCowaV1IkzW9DMUnLj73sFlv6iP7bJQXS/1NtWTOtcm/vplfJ65Ht152Ep1Txbf07kjuXTv/q/CM7LeuEsWEZbUkLfSs3vf4FJxzBK55zohOBV9PqNL4rneeCZChFVZWdt2hgIv9c9vJfErX8fWMfZnHnarO8J1VYbh1P0ILgAAW0tKB5ebjjvU9XB4TfHHspUaX9VKjb8aHNw/K0NManCR2y/0yaGn9w0uOaI+9/5eK8MC8z7lCajaXgZ1iMhUeFxXN9VKdU8W35MlO5cqqq/Kicutl0VoeR1t0Fd6du8bXFptxZF77heC8/ryARFg2t2zlPlNM2VmiOf9lEOd/pzxkg0upip9SEFwAQDYelI+uJz+oXFVF6vtumMZDxXl8FBRgjkiKh4qin8bZ6WhIv65alDIttC5++6EDfZawSVRGIjF4Wi/aEx5iKjuzxCVZfAcDf3Xg40ILmr9z91/K65j0Vxnpbq+b3BZbz1jh63i98VLOrgkCCmJtgEAwMeV0sGl7Z8f039/G1pT/LEsMjl3ueckETnxlt/iiRk+4Mm5OTw5dznwxAYXt8CTdBvbGkWDzQ2iscGl7k+e36KEFTXE9H7PQ1bae3zfQKCKDRz8JhX3MN3jN3v+Ut7subfEz6BWE/riA138eeKvEXvMeuu50nn7X4ZodEjbS5VscMn5+bkuDCG4AABsPSkdXDYyx4XxRNfMDCuNOq+S2tj1T4Sot4XDw1s5LLM/o5JGOyvlfn4VN/P7Z5oGLja4qL/nFPC3SDgQGRdcEjXyPK8mM+NS5A2n1cquR3ww4OvwN2TU18LVYbF731sjrylzz0wJz4OZuKs5T93RXPJPeeXH41TqR/7WqmeveP62b+op8CLa29Muwokp76rubTD5HZuMevkdGH/npcj2ZINLjYufv5UCXof8/d5rsT+vFsEFAGCL2dHBhTXyB+YOVkY/tpaRS8MtlZEGWX6ALvtSZH/N0cOaV2jjgws38qb0Mwl7BNYKLok+QKeemyePVuWJn5ei12bcUyCvFfMtl7UCwVrig4vc5nhF57LFtjnlw2/qh+HUeh4y59LMoHbYjc8Tfz/7+f6Xg5Zaz/gy6jPioFjR4iWTuTh6fAZ/DO9k5GN4KvXV6cx07fyXZIML9yxZm7y0N/0wZR6xiL+zhSw37iK4AABsMTs+uKj4k/Iz3Buwwiu3/tchCsytPadip1nruRmFn7+8ztLK1+EJvIG5jS0JMDMfxtIOAABbGILLDsLzeu7d90be4IkXnPDqjgEAANhKEFx2EJ48bKvuiXwzJV7Qm/i7MAAAAFsFggsAAACkjJQNLi7PKP39Pz/UbQcAAIDtK2WDC3pcAAAAdh4ElxQ3PR9e9U0bAACA7QTBJYWNvAvTnm+76Jo1j4IzHt1+AACA7QbBJYVdG1qgtE+KyHk5n4JLb3T7AQAAthsElxQle1sqHtCBPWYKuFt1+wEAALYjBBdhfDZM02MTuu2xppdEWBgVZZYWdPsYf7XVM/qGgrMrn4fX+PGMLdD46NiK81KmRSAZX+U6qusu7m0pJed59LYAAMDOsaODS7tngfaV1FHa7izBTAe+MFN7/RUKzvjk/vKeN7Rrdz5Zy4oo7dNSWcb6uZmmh7Q9HA08ZPOlTe5n10ryKTA2qCljF0Fj18ErkTLmPWZy3boSCSgDk2E6YOsUYSRf7t8n9l+/fIqmfY919R4XIWnP+ceU/Ymoiwu9LQAAsHPs2OAyMBumtHw77RYh4XRZKV2rv0kHzt+k8rxCCow+kGU4uKSJ4LJLlCn/uogOVNSI3/PoYp6ZgpNKMLF7Q5T22QXaw2Uqyml3/gUZPGLnnTS4RbD59JQsc1GUuVh7k/bkXaCHteUyuHBvzr4fBuVxxYX5dK22joqr7GTOKqXxP+p0dW/wiGvuKaf2ijwKvlu5hwcAAGC72bHBxTkpgsvnV6j4CzONuzopskjgu2gZNbh0/1AoQwj3dOyzDcoAMv5HjRI4xO/7+PeeGnmMiwNRgZ3KPxfhxv9Y6R357rFSpi8aQnhoSR0u4vkqu77ukmVcv9VEemECMXVRyTqIkCN7W4bsuv0AAADbWUoHl//N2UdTc+/WFH8s4wBgXu7lkENAB7PI2VIXGSZianBxNZUSBxueo1LQMka7dmeRx3GKXPMhEVJalWGmg/l0oLCcsoW0PYXKpFlvm9Kzc/AmFX/GQUbpyYnH5y3/bUJei8+VLcraa2007dMONzHZw/PpKXJ8i94WAADYeVI6uPzj33+nX253ryn+WBX3mNj7xujAdzcjoeH0l0pPCe9PGFwcY8RzYjwt5SKUhORwEw8lHcgvlMFFdfHrcjnk9HBGBJcv65QemEn9fJVYTs8bKq5qo7TPlPk0slflyU1Nfc1VLjLz9oHodgAAgJ0ipYPLRoaK4vFwze6KB8owUM8VuS0+uEyLbeZql5wXM/KbLTLEI3tXPG26czLXvAgu1lYZQpJ9bVnp2fHJgPSwukhsU4aOHD5lPo2jDL0tAACwM+3Y4NLtD1N2YR0NOGw0Pf+G7AMTlJZ3hcy7+U0dZe6IGlwu5osA0ddF1+645DBNMfeejCnDPhf7uEwRNXxXSAMDg+R84qLiqk7ytPGcF3V4SQkhFwvEeXo6ZZlyLvMbz3kJkUeEm+zzXeSwlVJgxkfdvgXa922r7MnxtJySZWRvS61LqV9MLwwAAMBOsmODi92tfT1ZZf82n4LzY7KMGlxi9/MwjaeDe2SUibUcKLLrXbrztF8ujPSKcDDZd/mBrozTxmXeyFeh95Upc2Vi8bBVYDkgtY+FKO1zG9m/5t4WpX4AAAA7zY4NLox7QwZ8C9TQ9pjs9lYacT3WfPhNDS7ttaXkuDNIzrZOCvj1awLJuTJ/jNH1hlZ5nnE3n0f7gblkyngmQ2S/46KGplZy/dElApTyOjUPUR1o8OjeTAIAANhpdnRwWUv8HJf4/ZuFQ8/1Oz5q/6ku0hsEAACwEyG4rGKrBBcAAABQILis4uFoiJy/PaDAmH54CAAAADYfggsAAACkDAQXAzjv/x+6bQAAAGA8BBcD3LD/qtsGAAAAxkNwMQCCCwAAwOZAcDFAKgWXso5J+uWEVfz8Srdvq6kZDFPOkeKI4GCzrgxsPb1CTk49/l4A8EEguBjAqODinQ9T+80+8fNz3T6jWFpeUWNRLqVCcJlZDJN/apbaBVP6VQo+qtWVga2Hg4spvRZ/LwD4IBBcDGBUcGl8EaZz6SfFz8O6fUZJpeCiQkOYWvD3AoAPCcHFABsNLm7BVt1Dlsv1lJNuET9fEurJ62yMlPFzGYeXco5eksMmJUeLafS+viv+3niYDp1olmUOCe03LlFwLhpS4oOLe1Gc90YPebv4XMl9ZC+ZuvROCU0Ocoq/k1qfxrPHRV28kTLOlyGynnVEhoJabWc0+yPn+mvlhrCud1Zcp178PBvZ5l4KU031XQq+fBbZttZziS9Tc0LUdTx6vLzWo1n5d3F31svnZrX1yLL3qosp2WfHhuf42LuR+27k+x6PhlX12bV7JymntHb5GqLM0qTmPGvVV17rdfRaVmG4TTzDpbe6conw/5et4v/LmqfD4vgz1C7+fo1u/rtXUiv/LZeiz892f1KW4WvUddaihwwAPhgEFwNsNLjwmkn+qbdU55qlivTj4uceOUQSnNc2MO1PX5Hf55b7bN2vKDNDNB6uaGDoFw32/uxG8nZWyjJeLtckGsQ/o/WLDS5eUd507DY5L1h1jeJa1qoL9x6Z0k9SVelhUW6Y+nm4p6CZvC3co6SUGZ4QjeOjZ+Ick9T/cpYyT96m9pNct2gIYasFF75OCfdSTd2NbKsaFLIt4p7c8vdknkurqEtmxiVyt12V9alwvqJzeeK5zEUDxcx8WGyfpSrx/DJPNNK9pkt06Mc+6v2e66x/Rolw6DN9c5f6b5yU1xnluji9NNOtf3Z1Jyzkf+mmdp94dnlXyd3EASn5+vaKgGTKqyVnFf8/9Yp6xXlqbA5NmdWoz935vZXuiWuYsuupXfy/0i/OZToiQvVTDowitDwNkSXDSqNDzfJ+LD+7xXG5Cf9eAAAbheBigI0GF9V6hoq8gqnotiYI/CL+BZ7Dx7v1PTEqNbh4xb+W3ze0xEtUF76XMq7LXE9km+n74VUb+XOP+P55v/b+Vwsu6rX9HZci2/b/6Kb+Gkvk92SeCx8TWzcOk6azfZrzMq6jKUM8v2blXvl59latfE/x5L1k1NOMs1K3TxX5/2Ap2oMi/25Hoz1lydQ3p+k5tX6jD4LJ4rpa+Lm/uB15zvw3iP1ZBrETd8n9czRUrfb3AgDYKAQXA/zY1EHD//V5UhZD/6o7XrVWcHG/DlNNyzM5XFEhmLJPasLCjJBZNUz7RcNqO3Gc3PdF47KobbS4ATwngsveUvGv57PcK/F+oWWtuiS6l/jgwo1t69CkOIdDnifnZP26gwuzts1S6wmlge7/S+ldCQ5Fh9nWei5qQ9xqK6Z7959FZF7+VRe0OLiUcR3neRK1vi7JsDpe0d70w1RWaqH+Noc4l3bIKtGziw11ydR3lMsc+1UErOO66ycrmeCiBrHYv81afy8AgI1AcDEAB5cHT91Jed/g0s5DA+ZL1Nt0SXb7D/PQy1GHJiyo3BMhqmsbpr1HK8lqFg2ZTz9UZBGhw5LB+27rjl9LMnVJdC/xwSXzhptshYdp1K0MjfEwzPsEFx42KUk/I4eLqobCVHeEe1v0b2at9FzUhrjiGM8vqtfg+Syx51ipV2i9+A2yRqebMr+pp0zxd5h5FL1OomeXKLisVt9EvWDrlXRwifvbJNoGAGAUBBcDbMZQkcUxqRkqSKZh4p4G06kezVBG7BwX2fuSl5v0nIfIOZKoS6J7iQ0ukX+p3482biuFgrUaQnXeSKCrknJ+fq4Ztkgk/rmowyxrHcdWquNG5Nzw0i/H+JxK71eiZ1fWJULXES7zPOn6xgfFlfD57g1NUuClMidIlUxw4Qm8piPNmiGqtf5eAAAbgeBiAKOCC8/FsHKDNa6cL7DI25W3VUo6ZqkqOzcy4bRdlDVlV2rCQv+cCBHdPaKMcgy/+WIqcmgmdcYGFzmEIho328H1hZdk6pKo8Y1tSHlIx5TdSP62M/J3rotFNOCJQoHaOEbmhSytUKezuZTDk0a9Ds2+ZJ6LOsE04FV6oLgxHx7iIKEdattocOEJ0f3OZ5GhqhmeOGzrI+cFPqdSP352meLZzSyHOrW+wzf4w4HJ15d7nyzpVppZnjQdENfqffRK8zaQci4OGrlUwj1wU9E5SckEFy6XKf5udfz/1KLSy3Xu/ltxPiuCCwB8EAguBjAquHDjc+hnt5z/kHnEQjkZhynoVhphbvD2lv5KmSIwZPLrr0ctdM7ZR7Zs0UAsKo0ov16892i9nMuRecQqGo/D1HiK3zSJvmIc/zr0qDhv5oU+auR/8S83PGtJpi5rBRdme/SW9orGN4fvNcdKzrZK2ntMNJIOfS8SlzWJspkHLVTGz+V1tIFlznlufCuproDPr72PZJ4LK+t4FbmGKcNCVUUW0ZBH68/Pjht41Wq9XSvh15MzT90Wf2Oui3Id29HDmleZ+dlZxLPLPHWJMnOUMo2losy89r7Wqi+r4DLmYtqfzXU+TDYuM6EtU+PiZ2clG/e+zUf3JRtc+PXuvaUOyjSLe8opptYbx8X+ZgQXAPggEFwMYFRwUfEXY2f4dejlHoJY/rkQBeai/6pWemXijp9XvjgbXEzuex3vK5m6rIV7AWam3kbulcNbcFF/32y15yKHT0QAU3twEknmuXB9+NX0+FfRjaZ+FTjRdWJDn3zGr7W9PrGSqS8/m7XK8LNZ7bkkw/86tOo1AACMgOBiAKODy8fU/yKkeVMllvcp9wroQ8PHxo03f8fExt8xiekx2GxGPbtEvVUAAKBAcDHAdgou6tdhE4n/Qu1WIOe/FDiUIZAEX47dTEY9OwQXAICVIbgYYDsFFwAAgK0MwcUACC4AAACbI2WDi3d0gjq6+nXbP4Z3S/+i2wYAAADGS9ngspV6XD6maX4bJMFbNgAAANsRgksKG3kXpj3fdtE1ax4FZzy6/QAAANsNgksKuza0QGmfFJHzcj4Fl97o9gMAAGw3Ozq4TAvWJg8dyCqkaVerbr+RKvve0L6scvLcukDJfs9jNbK3peIBHdhjpoD7w9YdAABgq9jZwWUpTPt+GCTzbrMILnbd/lge/wJN+8d021X8ddKRsTcUnE/c81F8Z4J27c4jj+MUrRZcpkUgGR+doODSgm5frOsu7m0pJed59LYAAMDOsWODS/FvE5QmgkSaCC2xrheaRfjwRcp1+0O052t7ZH/xl1k0PhDt4RgXQaPcPkhpn5fK/buFi18X0ciTTuKA0uANUdqect11rH8zU2C0K3KegckwHbB1ijCSL/fv2yPqcvkUTfse6+o+LgLXnvOPKfsTDlzobQEAgJ1jxwYXp3eBKhvaaNfBKzJsVF4up+sNdvL83hbp7RiYCdMuayvtEvvLSwrJXHJFhIosqjwows2MS5ZRA1BBlpmuVV2hiz/Zac/BCzRQXy7Pw+e4Zn9A+8rqZCA5XZJP1+vt1H1LBI75CXkOtedHBqPCfLpWW0fFVXYyZ5XS+B91uro3eJQw1F6RR8F3yjkAAAB2gh0bXNhaQ0VqKHlYWyRDiCxfNUj7uPzATTk8lN3kk4HDWVtKwdkxeRyvnRP/ivJqQ0U8X2XX113yvK7faiLBKfBOX2fubeE6y96WIX2dAQAAtjMElxWCi9xX7ZKhJDsriw4UlktpXxTJHpqRDpssZ+fej09PyXJ7RJi4dr6cRga61hVcOACVy5CkDBNlf2Yme62Npn2DujrbeehJXM/xLXpbAABg50np4PKPf/+d/t2/d64p/ljVmsHFpgzfZH+ZFwkuzPpVOY33RcsP+EN0sekB7cpTAgwPLbns2oCyWnBROT1vqLiqjdI+U+bLyF6VJzc1dTJXucjM2wei2wEAAHaKlA4u/9T1hBb+x19rij9WtVpw4V6QA02+5d4VfoVZf3wi8tsqu0t1k3wjwaWlnFYKLiq+dkELD0Fl0cPqIrFNGTpy+EIi1FwgRxl6WwAAYGdK6eCy0aEiGU5axmQPiaO6lB4ODFJ3zyAFZ5TA0T4qgsIXV+j0QTM97OsS+z102v6AnNU2GRz4OzDFDh9VflUk3/5xTYao4KfHcl5MOw/lLEXDhRJoiuhaSR49fPKYnH0ucYwywdczH6bs813ksJVSQFy727dA+75VJgV7WpQeGtnbUutSQlZMLwwAAMBOsqODC3P6w5T2ZY0cmlGHeWKHcy7+8UZsL4zsZ5X5ZgpOuuSr0AU/8XCSMjdFxUM8433acOGRH4zr0pRr/y5fBiB+FXpfWatmHzv9pZkCYw/k8e1jIkR9biP719zbMqa7DwAAgJ1gxwcXNjIfJkePh9pvddK4hyfEaodynO43dL2pjRoa7OTq6xLBQfvBt3FxfHufT5TppO6ONgpMjumuwbjXpH1gjOyOTvI8eaD7yJxnMkT2Oy5qaGol1x9dkY/Zcc/OgQaPfOtovE//ejQAAMBOgeCSAjjwXL/jo/afRGiZH9PtBwAA2CkQXAAAACBlILgAAABAykBwMcDIqyndNgAAADAegosBbth/1W0DAAAA4yG4GADBBQAAYHMguBgAwQUAAGBzILgYIBWDy+hSmKzVz8iUbaVMcy7VfVNMwUWvrhwAAMBWguBigFQMLpk/uqn9rIWC869oZjFMMxOTmv1e/qjezT7x83PdsUbyC7+0uCk4NazbBwAAEA/BxQCpFly8gqnoNnlbTur2qRpfhOlcOu//sIGiV7Ck11LwxW3dPgAAgHgILgYwKrgMvw6T1XaXco4Uk1UYbhMN+tLbyH4e3im58UzsPx7d/1d0f++U0OQgp3g2h040y/M0nj1OwTntENBqwcUt2Kp7yHK5nnLSLeLnS0I9eZ2NmnIzwrk2r7jGmYR1YffGw5F6HBLab1wSdXkl93FPi61pmErEufenF5Pt8kl5nf7met15VsP1bRf17X39XFzLobtnXkizStTT3cnnjanbRJh+qXZgeAwAIMUguBjAiODSOyfCRF4tOauOk3/qFfX6ZqnGJhrWOaXHgxt604m71H7BKve3i/2mvKvkbY6GD+4lMaWfpKrSw+T3DVP/lChT0KwJKDk33JQpGndThoUys3NlQ18jBP9yy/3c0Pun3lKda5Yq0rkuPcIsBee1YYKHmqqO5SrXeTlLe49pr9MvQtb+7EbydlbK470CB5Xgn9Fn5X8donax/VD6VfK7HLJcYG5Wc521cI+NKb2WKo7wPffIuphEXZwXckldc+rcIxFesvl35R6ZtW2WWr/hbeu7HgAAfFwILgYwIrjkND1ftSGt84rGNl0EjIm7kW3cINsy+Bgl3HBwKePhnbmeSBnT98PU+z2XiZ5rtR4X1WpDRa1TPLxzSTO8U/cnh4NoAPplXNwTH+9u1h0fa6NDRXz8IT7eFz2en8u5dHHPS8+UMhyiMkSZIaXXSA2B/rYzuvMBAMDWhuBigB+bOujF+HRSFkP/qjt+VDAd+5W8zcd1+1Tn7ut7DThcWDgcLDf6icLGhwguHAysIhjcu98sPJNqup+JupyJ1IWHkjKrhkVgyCXbiePkvi+2L+pDmRHBJf74+OfC9te4qf9Hi/yZg1cJB6+paAgEAIDUgOBiAA4u7XefJCVRcEkmSJR1hajxKAcQZY4Ii2+gE4WNDxVcckRwUee/qOqE+LeD3BMhqmsbpr1HK8lqFvXwaXunEgWP9Uh0fPxzYVWDHPw4uLippGOWnGejQ0kAAJA6EFwMYMRQUaKAEatqiIOEJTL8oW4r423z/Npy4rCR6LwbDS48LFTGw1bL100G98CYTvVQb5W2LomCRyL9L0M0OsT3rg0biY5PVD+ec5OT3UiBP5vJdLaPAl2VumsAAMDWh+BiACOCC4cQS7qVZlzKnJCAaGh7H70SQUXpYeGG15TXGAkbMzxvw9YnQgn3IiiNeaKw8b7BheeoWPlc48q9BRZ5u3IdefyxX+ne99bIW0/8RlTQF31Dp39OlOvuEfuVY9yLfE0HuZt4Hkz0Ohw89mfUU+Cp8tYP37d6TGwZkyhjSs8lf+cl/T4RXNxyknIo8lzaT/I9a4em9vOE4ppiqsioXFfoAgCArQPBxQBGBBdW0fGKTOZi2p+dKxrjw2QrEqFkIhpCWn2ikT5YSTk5h0U5C9WVHta86mxkcOG3iw797Ka9oh6ZRyyUkyGu5XZE9nMw2Xu0WX51d29OMeWI/7rbuBdDCR3OlyGxv17Occk8YpX303jKqns1m5V1ivvOsFLmQQvtzbDQTFxvyPBfHNrEtURwUQOOioNLjgguh05dosxsi3wuFQfF/U7ogwn3xJjSizVvHAEAQGpBcDGAUcGFqa8jx79+HItfI17va8PvS35Vl1+HjusFUfnnQsr+FYLAzDzfj9i/uPL9MO5pkfe9QjneH5jT74sdKuJrrVYX/ubL/gIRvga136QBAIDUgeBiACODC6xPojkuifhFALP87KZfjh2m2AnOAACQWhBcDIDg8vEkE1ycIrTsTb9KjWeLEw5VAQBA6kBwMQCCCwAAwOZAcDEAggsAAMDmQHAxQPPtbt02AAAAMB6CiwHQ4wIAALA5EFwMgOACAACwORBcDLDTgku/UHKkmYIvsEghAABsLgQXAxgVXLzzYWq/yV98fa7bZyS/8EuLW7cgYrKSeQUZAADgQ0BwMYBRwSXRJ/s/hI0Gj40eDwAA8L4QXAyw0eDCn6K3VfeQ5XI95aRbxM+XhHryOrWfpucVls+1eSnnyBmyHimm4TYRHv7Sfgb/3niYDp1oFmWK6ZDQfuMSBeeUL8VyT4utaZhKxLn3pxeT7fJJeZ3+Zl7/R/85/ZWowWXYfZustrvyWrbSYgqOR1euHl0MU9nNPllX3n9O7J9xa4eW6h7Nyuu7O+vlIoxWW48se6+aF2JUPttv63xOM3/2aO579L52vaKNPhdVzf1Jyjl6SZYpOVosnj8veJn8c2FqfUtuDovzHKeKo3zfMStX985SbxPXP7pkg3tJXLtaPJuX0ecHAACJIbgYYKPBRV2fqM41SxXpx8XPPcr6PnHrFWXy6sbHcsnvG6b+l7O091izZqFEXkF6f3YjeTsr5fFegYNK8M9o/Xido3ax/VD6VfK7HLLcetc9UldkLjtymEaHbtOoOIeyUjUvXrh8HS5330v+l165v6TFTSUZVgqKe1PL8NpCFc5ZqirKpcwTjXSv6RId+lF7Hl4kMjODF3AU9Z2apLLOSTonfg8uRXuljHguVYMiaGVbxDmUZ9/rm6Vfqh3iOusbtuP68oKTXudVed+8zEAF13d5NWruVSvhXrWpaIjja1eJaweX3LrzAQCAFoKLATYaXFSrDRW1TnEvxyXN8AyvdlyVzb0TSoP3yzivlCyOd3NPgf78qo0O9agrMsdex9LyihqLOHAkXgdIDTvBR9wbEt1+7pHYLhp2b7MSNPg8vVXa4DJ8g+9R+Z2fkYXvcbnuRj0Xi2OSao5wINrYkgBcX2/z8cjvvUt8f+Ke7yv3ra7M7e+4FCmzXwSv/hqL7lwAAKCH4GKAf2j6J/rjmTspi6F/0R2vWi24cANvTc+le/ebhWdSTfcz0WifiTTaPGSSWTVM+0UQsJ04Tu77YvuivjfFiOASf3yi4NL/MkS2m3flcBAPT5nSixMGl7L0aI9EPBkEYnpP4oOLUc+ld05c62A9HcrOpcbqS+R387BN4lWmVxNfXzWoxG6zts1S6wl+VrPyDS3uDQoOYcVqAIBkILgYgIPL6R8ak7KR4JIjGmh1/ouqToh/O8g9EaK6tmHae7SSrGbRQPq0PUKJgsd6JDo+PrjUDIXpkNlKbme9HOLh4SlT+tWEweUcB5cE98zig0Ci4GLUc+Ehu173LJWJsGUyH6dfSg9TcClxD9JK4uubKLi0TvBw0Rk5XFQlnlPdEe5tWd+QFADAToXgYgAOLpNvFpLyvsGFhz/KuMdihZ6JRLinwXSqRzP0whIFj/VIdHx8cDFVDdM9W/S6qw0VbSS4GPlcYrVzD0x6JQWfaicCM/dr4ZGo75J+4m58fXnitelIMwW6KiPbeP6P6Zu7clvOz8/J/XN0KAwAAFaH4GIAo+a48FwMKzfK48r5Aou8XRmukP9yP/Yr3fveGmkwh0UDGvRF52T0i8bW290j9ivH8Js6piIHuZu0DSOHiP0Z9RRYbpQDS+HIMclIJrjwvI3Wb5ThEP69xv1WBIGThgcXo55L++BbCryIhp86b0iZF+N1aOozunw9k6jz8A2rZh/j+jYeE/ezqPSgnOt+SyUZFs2kZFbSMUtVZ3Mp50ij7hoAALAyBBcDGBVceKji0M9u2pt+mDKPWCgn4zAF3dFGjRvgvUebKdOcS3tziuXbK+42/pe80iA7X4bE/no5lyPziFU0roep8ZRoXOf0E07LOl+RKcNKmQcttFc0rDMxPQJrSSa4qHNGcnLEvRwsptZTxWRp7qNfjh2OlOFjOACoYgOKaq3gwjb6XPi527on5fBQZrZyDn6TabiFz6HtVZG9JSd7lPo6Ete37EQx7c8+Ls5jlefxd1/VlXPOKz06dQX8zDBMBACQLAQXAxgVXFQziwK/Dr1CL4h/LqTsX2HyKL9mLF+nXtQPZcTinhZ+DXutchvBr1/HvtYdWExcZyMY8Vy4vqudg3HQCbxOfA41aK31bPkcpgt95G87o9sHAAArQ3AxgNHB5WPqfxGKvJ0Tz/v0/d602Unie4gS4VBT4XxFtjyrCHWJh8gAACAxBBcDbKfgon7NNpH4L76C3lrBRU7WLXCQrcii+dIwAAAkB8HFANspuAAAAGxlKRtc/uv/+4ra7j7Wbf8Ymv7jP+u2AQAAgPFSNrhspR4XAAAA2BwILh/J9Dvx33eY6AoAALAeCC4fAb8KW2D3kfWLPAp4OnX7AQAAIDEEl4+g2x+mtKwaqjxopuCMS7cfAAAAEkNw2WSyt8UxRrt3Z5Gn7QLhuygAAADJQ3ARxmfDND02odueyMhMiAKTicuOTIZoxDtGwXcLun2qh5NhSsuro8o89LYAAACs144OLu2eBdpXUkdpu7MEMx34wkzt9VdEoPDJ/RcHFsT2Qrmv/adSyv6hK1J24KciUntLHvpDtK+sVW5nu7n8D6UUnB/TXI97W6y3xmjX7jzyOE5FjgcAAIDk7NjgMjAbprR8uwwZp8tK6Vr9TTpw/iaV5xVSYPSBLPNwLETW6s5IeNnFoSQrX/7saSknDh4PZ8K0q8Aut5V/VUiVP92kfV/VUENJPgVnlQCk4rJpB2/SxS/NFJwc1NUJAAAAVrdjg4uTh2w+v0LFX5hp3MVv9iz3fvBryjHl2sdEuU8v0B4RTEbuXKHKoTe0+5MiGum4EOlB4V6YgQYOMjFDRAledS7+bULpbWlBbwsAAMD7SOng0vbPj+m/vw2tKf5YNr4UJvMPg5HhHevBLHK21EWGiVRqcFHnpIzMh8nlEmVmxuQ59lwelKFmuq9Od41YsoenwE6ns8R5/OhtAQAAeB8pHVz+8e+/U6Pj7prij1VNi+Bh7xujA9/dFOFFGQI6zcM4/uhSAmpwsZdkUfCddlKuDC7fPaB9HFwGburOH6v89ze0S1zDZVeGmOL3AwAAwNpSOrhsZKgo3si7MO2ueCB7T8Z7rkS2rxZcpgVzrUvOffHcWvnVZtd8mHZZW5d7W7bG+koAAACpaMcGF/4IXHZhHQ04bDQ9/4bsAxOUlneFzNx74rLLMiOzYar83UNpe0rpYr6ZXE8eUHBGG16uDS1Q2ielVPCZmbo7btLDARedtj8mZ60IP+/eyDKne5Z7W5rQ2wIAALAROza42N0LtOvglcgcF5X92/zIa8yxr0Oz+N4Yxr0uxQ5fZKhJVVnAbw65yMO9LSVtVP6F+H0MvS0AAAAbsWODC+O3ggZ8C9TQ9pjs9lYacYlgsRR9M4h7XAaGfIJHcgnxPS7qeZzuN3S9qY0aGuzk6uuK9LZcfKKEn4H6UtK8dQQAAADrtqODy2ZwuESg+eEm3iQCAAAwAIILAAAApAwEFwAAAEgZCC4AAACQMhBcDHDv0X/RbQMAAADjIbgY4Ib9V902AAAAMB6CiwG2YnDxvw5RcPGtbvt6zCyGKfB6VrcdAADgY0FwMcBWCy6/jIfJlH6Shm9YdfvWw1Q1TCXpuRR83aPbBwAA8DEguBhgqwWXGaH30SsROJ7r9q3HsAhAo0PPaKVlCpwvQuTudOi2AwAAfCgILgbYasFls1haXlHv97m67QAAAB8KgosBtkpw8Qu2pmGyVddL7s56XZm6R7M0+shBNd2TlHP0Eh06UkzDLZViX3Q+TLs3HDlHnRCcGtacQ92//9hVKinIlT9XcTnf5g8puYX26h7qff2cDp1wUI64n8azxyk455X7eTmGqjav7lncmwjTL9UOCi4q5QAAIDUguBhgqwQXxpNy/VOzdOimN2FvCPeS7M3Ipd4fz4hyr6hmaJYs6cUUfHE7UoYn5fI52qd431XNvtj9fI32y7ny5xkhuJR4SOlD6v2L5/PUUsWRw+QXwan/5SyZjjWT8wLfu1Kfc49EeMnm392R46xts9T6DW/D5GMAgFSC4GKArRRcVCsN4/D29lO8XelhURv+4KNaXVneZ+F9ccFlrWtsJq7jIa6jL1pHDirneFLxEs/PEWWWwrQ/Q5QZapS/c8+U6cRd8red0Z0PAAC2NgQXA/zY1EFu71hSFkP/qjv+Q1gpVMRv3w7BJb6OjS9420nNtv01bur/0SJ/bp0KU0n6JQpO3dWdDwAAtjYEFwNwcPn94f+VFAQXYyWqY6LgUjXIw0UcXNxU0jFLzrPRoSQAAEgdCC4GSLWholQMLv0vQwlfzU5Ux7o/w1TG83bm+6LHL4UpJ7uRAn82k+lsHwW6eEKy/joAALC1IbgYYMcGF8ck/cITXJcm5e+BxQ/TgyHrmFEv6plL/s5L+n2iju7mk8ShZobns9j6qP0k36N24u3+H91UVVNMFRmVmlADAACpA8HFAFsluHgFU9Ft2cDHaiziRvyVLJNMcOHJrfHnYPHhpn8+THuPNlOmOZf25hRT3RE+r/GvFw8LpjxxHVGHwFPta81c/xxR/0OnLlFmtoVMZgtVHBT1mNAHE+6JMaUXa944AgCA1ILgYoCtElw+Fv9c6IOvaRRYEub0ay/F9grNiCAlX8teIZTwN1/2FzgoOKi8XQQAAKkHwcUAGw0u/S9CdO/+sxX902//u25brMAL7QfiPjZ+3fjefa+unqqOLvHff/5dt101fJ/nsiQXhNYazorUaVGU+9lNvxw7TGrvEwAApB4EFwNsNLjw12zVL9UmcvL7Kt22WP5HW2u9IO7ZsFX36Oqp+q5S/Lfyf9FtV7VX83BQcussJRNcnCK07E2/So1niyNf1AUAgNSE4GKAjQYXAAAASA6CiwEQXAAAADYHgosBbv6HO7ptAAAAYDwEFwOgxwUAAGBzILgYAMEFAABgcyC4GGArB5fM6mHqv1Gs276SmsEw5RwpjggONuvKAAAAfCwILgbYysHF9P1wwk//r2RmMUz+qVlqF0zpV3VfywUAAPiYEFwMsJ2CiyrRUgAAAAAfG4KLATYaXPgDdL33HXTo7F2yHikm72AzWaufyZ9nYoZqRpfCVHLjGeUcOS73DbdxqNB+Bv/eeJhySuvlME+77QyZLjt0wYXLHDrRLMvUnDhOwXH+Uq22TmsFl+G5MFltdyNDSo3iWsHx9X3Bl+979JGDznU+F+c4I+9p9H50LaJ7E6JMtbj/Ke15bR3PRTkMYQEA7EQILgbYaHDhhQ8tGbnkd98mq0P5eXSomcraJumXYxw6JuVn9E0n7lL7BSv5p15Ru2+WTHlXyStXRVbO0zvPixHWU//PJ0WZSaobmiRTxklNcGkVYSAz4xK5267KMhXOV3Quz0rBOW04WC24yLp8c5f6byjXGZ2aJZvTSzPd6wsTfN/7xb32N12K1CUnXdTFq3wJWF000t8RXRG6n1d/zm7EekMAADsUgosBjAguarjglZnV1Zxjf67zhsmaXkzBibuR43i/LYP3K6GjpGN2eYXm6Ofy44eK9v/o1vwe4DJn+zThgK0WXOS+jHqacVbq9q0H3/c9W7QualDxNh/XlGk9wWWUtYuqhoRsCwWX3LrzAQDA9ofgYoB/aPon+k+/P03KYuhfdMcnE1zO3ecGm3+ONtiNL3idnpORdXpMVfr5LLHBRQ0GrbZizaKGmZd/1R23WnBh3DO0N/0wlZVaqL/NQcH59S9cGHvfqvigxT1EJelnKDilBDYOXv0/WnTnAgCAnQHBxQAcXM7828akvG9wKesKUeNR5Wf1OF1wSTARN1FwqThm0S1s6O6Mzi1hawUXeb55UQenmzK/qafMjFyaeaQ9x1qSCS7qsBT3CPWLn3N4mOjP9Q1JAQDA9oHgYoDNGCriIZJz6TxEEp1Iy9vKeNt8n/w95+fnmmEVFhsE1GEh989rf9clmeASK+eGNzIfJ3b7zJI416PnFHytX+05PrisVD9r2yw5z+ZS3Z8hquNvyyS5cjQAAGw/CC4G2IzgwpNSTXmN5G1RJuNyINhv6xPH8bBJSG6rcXEPjJUCy5Nb773mY2o14cD2NESWDC6j9NJwWBge4rARDTvMLZiONEfnsSxF93nFz/1OEaAWlWPUujgv8HWUuqgsjkkRgHKpJo/3ebX7WnhisNj+Wgljdd4QZXIPkkvbo9I6xQHtEuXUNJK7ae3QBQAA2xeCiwE2I7jwvlafCBMHKykn5zCZzBaqKz1MwbloGJgRrE1eOfck84iFao5ayHLjrm44pqzjFZlEeMk8aBH/tVBVkUX3yjGzPXobKVeWIa71ukduHxaBKPPUbXGdXHkdPoft6OGEr1WXdPKH7HKXe2O082D4vkvE/e0X97RfXIPP524+Q/HhR+2JyRH71TeOAABgZ0JwMcBGg8t6+V+HKDCn7SGJNTMvGvvXK+9ngSX+Qu5bCs5rvwMTj7+kOzMlzrWkDRPqPv7K7prnmAslPF4NbBxM1qpLRXeIWr/h8LP6fQEAwPaG4GKAzQ4u20X8HJeVtL8IUWbeVQo8Xd/kXwAA2H4QXAyA4PJ+kgkuOU3PyZKdq/miLgAA7FwILgZAcAEAANgcCC4GaL7drdsGAAAAxkNwMQB6XAAAADYHgosBEFwAAAA2B4KLARBcVsevbwcXV37VGQAAIFkILgZAcFnZL+O8dMBJGr5h1e0DAABYLwQXA+zU4OJ8ESJ35+pfsuWv+fY+epVwrSIAAID1QnAxwE4NLsl8hwUAAMBICC4GMCq4tLrfUk5pLeUcKaZW2xnNOkS9r8NUU32bgj5lvSDWOPiWnD/XU3AxugYQfz6/pnuSco5ekuepOXGcAi+V1aNV98bDdOhEc2R//BpDts7nNPNnD5XcHBZljlPF0WKacSuLMrJ2ryhTXU/7j12lkoJc+XOVEFs3P5+naVjuY+7OxB+Qi73n1epyrs0rypwhqygX/zG64bkwWW135TlYIz+7cf3aS6upezRLo48cdE5cL9F1hhdFXWruUtAbvUd5XO8sDf+dy+mXNAAAAOMhuBjAiOBSNRSWqzZ7HzXS6NQsWX52U+OxwxRcioYS7uGQiy6KbU7RWGdmVOo+gy8XLszLpdGh2/I8NqeXvI7ayP7WCT7uErnbrpJ/apIqnLxCs1WEpGhDb/peBBZzLnmdVyN1qcgQ151XApC6RtGhm15qv5wrf060nhFPylXLJeqZUe95dKg5cp1z2aLcXDS8cF0yxbXV+pZ1TtI5rsuSUl8OSKZv7lL/jZNyv3rPM93aFabXws9tvzhvf9OlyHPJSbdqFnXkuvT/yKtxL9/f8rX9bbwwpP6cAABgPAQXA2w0uPz/7d3fS1vrnsfx85fkzguJUMiAECyoCDsMNPTCWNgVQSxF2VgI7guLYCmodGgoB3v2TIRD68iWE0qP9QhSmbQUmqEQKGcC0sqmHU89oqMoHSdKD9ur7zzfla4kK4kaa+z2qe+LF9usn89a++L59PmxHqcC7HokmZ+689vShr/NVL4vY/ltmd19qWt/IKl4t/ijz00l6h3wmtg25zTclOyLwjml/LfTnhDhrry8PNWf36YVdGb8av73vLmvr8GEn7lCAFLVdhVVOs657w9PJTlcCAIZ3XbZBK544T1oWVIjkfzv2FtzvXqz/22uBWhej2kYk7XEQNl9j0PLOBMtlNEtS/F70NW6BzVYfUo7vydW9yVcb97bh0dl1wMAnA6CSw3cvjcl//33zars7P1adr5T+dbfkpk712Vm7rkjYfiujHvCjIotmmMvdMvod9rq4B3wGn1mKtd63e7tbnG5lfFENJK/jwrc+NkTLJzgUnTffCVeUpZKgaSSSsc517z0wBOYlN77sLKUBhcVjr+TuvpW6bwSkuTDuGS3C61U1apUxtKyJE2A8zfG8mGyY2pDJrp0PytWA8DXQnCpAQ0uE9PzVTksuES7I/kxIa7lBe+sndHX+1J3ISJ9ja2eLhWlLQJOcPlUeXyHG0B62kNl9ykeg1IaFk4juGiLkk9blEpacUrDQmlZKgUXldk2+xJpCXw/5nQtrS1UHlNzkEplLC2L8g+nne4it5Vs6/HJWnoAAMdDcKmBk3YVuZX4UZWg/os/cDEmSwu3JDCYkkSvVqqFD7sdVKm73G6h9J1C10slpWHhoPJVquwrqXRcvnusqCvG3VZcvtKyHPWMKjiSkfvter8Vz/a1XZ2a/abi1OzSMh70rgZfmPDYFpLE9hvprB/Ij/sBAHwdBJcaOGlwUaG4DpI1Fed6rhVFK9nMq8KsIv0eSsBU4jNRHRPyUWY2TcXaeMvT1eJW/JO95pidXKWd/LAna+lCC0z02Z4zIHYrk6v4tYJOvdRjC90dGhZiWvHv5Cr4vicfpaPBXHPVO6MmFF+R+9+b43Zz99raqTyzpjQUuLSrxXnmzwODRzN7ZaHkqOCi436SCfPOdnLl1/fmjz6VxA96P295tLy++iYZ1nt+KrxbZ99P3vevZQnofV55B/kmjWBjTDqHYxXvAQA4XQSXGqhFcNFg0jKSdsZqBMy/6PW/E72RQnhY+Ch9jTr7p9A91Df3OVC8LwwOTZpA4788bs5vMsEm5MwOSse1paRQwXZOvROfCS+B5pD5b0gGL2so8c4q6uyKiL/xqtQFw07Xy/KTm2VlTm7vS92lcQmYe9QFIzLaVggEbveSBoVizqyoT7kxKO4z+xtaxd+cu8/SY+99jgouqXUT6K49cJ5X35s+T/RSa9m0atUxveGUIdca4x0H48zGMmXzNw8Y+v7NexvX2ULlwSR4541zna0K7wQAcLoILjVQi+Dicqcan3RtnzUTKpwpyhUqXrW1q/cx99guv48bFvLHHFGW5c092Vr/8gGq+syVplMfR/69VXgez3GmrJXu47YKaQvUQe/FNZrR2UUmVO7mZhcBAL4egksN1DK4nAWlrRznwUHdWaW0662ufVwyRVO2AQBfD8GlBggu9qsmuPQ82XO63lI/adfbwS0yAIDTQ3CpgW8tuAAAcFYRXGqA4AIAwNdBcKmBnyb/UrYNAADUHsGlBmhxAQDg6yC41ADBBQCAr4PgUgO2BJeJ9/sSbBswIo6lqcOXGAAA4KwhuNSALcHF/aBcanVDfJfi527KMwDAfgSXGrAluLgOWu0ZAICzjuBSA7UILvdfbUhL15jThdNizIz05xcvVLpC8+TQrKTW30g4+sg5Lnol4lmTZ2lnXzrvPjX7rjv7+8z+tXRhHSPXYcFl5sO+jA6Ne9YuUtGpN7I0V1hwMDr9RqJDYx7p6THPOUu7+9Ix8tyU5ap0XIp4zlejCxv589Km7OHorFPumSFdkbn8s/yVuO9l3ryXlq64c36s96pkN3NrJukn/AcfZsrKps95fygu2R3vYosAgLON4FIDtQgu84smULycddbbSSxuiO+fxyQ1Ei7sN3z1t6SnuUmWTBhZ0u6e3lnP1151dej5uYws/5Jx9nf8lJaOhnDZqs6HBRd3X/Gq00ldcbkxJtkXsfy2mfSGzMw9d4w+eS6+f+r3XM9dqXrih7BTnknzTIGLN2Vt4Vb+GF1PqSexIYOXmyTQFZOZe/3ScvvpkV+wLZZ/L22tsrw4K8lfzHtpH/es3Ny3oGsL6e/C2kLhhxsyoStbF62KDQA4+wguNVCL4FJKP0FfvJKyVtBBU0Fn04VWi9JjSrmVerYoLKjDgot73YmuQqU++FIr/tCBiwrqaskxXXF5t1AOPadPV67eLbTcdD7e81xXaajwNTRJZjxXFufT+4PHCy4t+oyLudWi3Wv21Wt5cq1R8xq8GswxL3PByw1Vyw919efyawIAzi6CSw3cvjclz/4zU5WdvV/LzldrpnKNzWn3y7jTfeJvv1kWXEJaQb8tVNCVgkvylz2J3n3kXKPD8NVHjh1cJj7sS0e9qdRXc91M/ttpSd4OlR2n+hY+Sl9jWLKbhS4rpWXra2uSmbmf8y0zPfHnJlBoK1IhzGjI6NSQsf207NrVqPReYm91W7dnm3+48AwTq/p8/fnnAwDYg+BSAxpc/iP116pUCi7aAlDXPSuj3WFZXkw53UUtdzPHDi7DL/el5UJY0okxc40VmdTupPqbxw4uTovE94+c7qKk+Tuo3USvveNTVGJzXwINA57uH5eWLdTYZALUTc84mMkhHWvyJn9cvnWkKMwcR6X3Uim4DL743Gr0KS0dUxuS6NV7VjeOBgBwdhBcauCkXUX332t3R7enu6M0lFSqoEuP8Q2mZCZa6Gb50q4ipWNAtHIffb0no206WLYQNpxr7JprtD+Q9B3dV36+dguNtmlZvOeVqja4aEvS0ktt1fGGjUrvZfS1tuJEPK04Ok5HA9iWCWC+3qey9Zhv2ACAjQguNXDS4KJdF37tuvg8+FVn4/h7Z48dXLRLp3jA6XD6owku3WXBRWfaaOWdGikKHbvlZeo0ZQoOxyR9rzycVBrXUmx+29zj4piknbErubCh4SP7wTuLp5rg4gSwBu32apLl6cKg4fw+817c+2iXmz/6VCa7C+/Bpe9ncDgiPQ0DX9w1BQD4bRFcauCkwUWF4+/E39AqwbawtARDMvlkXPwXb8nWQm4abzXBZX7TVOLNYxIMtkqgOSIT1yISGn8q99tb88e47i+aYy9cl4Aeq4Noiwb9KjfcBDVUZOKefW5Y0CBRrLi1R03oPZoHJNBo9jeGna6j5WeFmUla/uLzD2oBSun9Lo5LwByz9cw7rdkdtNxyrd/cJ2SeKeTMvMp+KA8m2hKjY36KZxwBAOxCcKmBWgQXtbZjrGorQa5S1S/dZnePX8Eur5tztj/mf2/tVL6G+yXd7E7h2GI9T/ZqMmVYy7O1frJraFm3NsvLWRzodHp18fsrpd988X8X90zrBgDYheBSA7UKLmfJ5Ns957srpS0cZ02llqhKlk0oDN1JV2x9AgDYg+BSA99acAnee+N06yzNne3QoqoJLgkTWurqb0qsN5L/oi4AwE4Elxr41oILAABnlbXBJfP2b/Lvj5Nl238Ld/7wp7JtAACg9qwNLmepxQUAAHwdBBcAAGANgksNOdOQD5haXC2d9rumU5QPmNILAMB5RnCpEf1sv36lNjWiiwiW769WKL7ifGgt+6p8bSAAAM47gkuNrBnzC+8ku155bR5duPD+T2nJrh78aXuV2dyX9II5ZvdkLTcAAHyLCC5fYP7tnmTfpsu2H6aa7418icy28eLwMAQAwLeC4HKEeV25uTcuwbaI+JsjEgyGnL+XpnKrC2tLSvReSqJDY470tPejbe7+DrPPXx+R6I1u57jkuB5XaFWZXzXHDcXz18lmZsvKoosv9phrBduuSsCUQdfm0bLomkTZTyvOJ+0nh2Yltf5GwtFHzr7oFbPvva6qXLhOanM/v7/jknmWOW+31OjCRv5Z0jt67Kxz7MyQ3qcw9mYi/VGCV27lyhC9zsfdAACnjuByCF3h2H9xTDLTA86aQYkPexJqviXZRW+riQ7KXV7dkJa7GZn/Udf28V5H90/q/vqbsvwq7hy7teldu8ddNyhl9vkuxSuu6BwYTMlkb0iy2++cT9gHfnzqWZjQXfxQFxlcSj+SJb1W76ynTMldXbAwJsk73eZ+KzL6ckX8Dd2yNle4n67505PYkMHLTRLoisnMvX5puf3Uc53Bl/sSaghLZiHm3Ec/px/Tz+kfsFo0AAC1QHA5RN+CqaAbtbIudAv5b6dlfrA8nChd7bhScFHVdhVlDN/lB2XBRc/36/kvCwsEaniI6srOn3JdRe5KycUrPZeuIK0LJzrPtFt4Jj3mfrses5Lfps/ua2iSzHguGDnP9vm5tRXJ1/XIE5qcBQzbxj3lAwCg1qwOLlN/TsrO3q9HKj23WhoMOuu1heNpfpsv+lyStzUslB9/msElqdsbY7L1ONdFpfrmvMGq0j1Kg0vL+DuZ6NLfhRYfDSl9OpPpcwByt3XqtqJnd7ktOzN3rsvM3HNHwvBdGfeEGQAAas3q4PL7P/5ZxsanD/Uv/5ooO7daOlNIu2eGr4RN5fxIOu7NSsfFsAkG5eNP1GkGFxVd+CjhZlOWh+MymngugYv9kpnuP/QepcEleOeNzES9ZTwouJRuK76PBpdodyQ/Jse1vBAvOx4AgFqxOrjUqqso+cueLL3UAazej77lx5UMdzutCukFc8yOd2xKsVMPLs/2ZPCyhqhZmTfl2frgHQxb6R6lwaVjakNilwq/3W2jbbqtMJX7sOCi3UK+tnFP6w8AAF/DuQ8uTutBw5j4TCW9XNR6odwQ4QYXtbao3TKVv2p7VHDxm/tsPcvNOtLBuDrgt/S4w4KLXl8HzGpw0bJkNGwVfam3muAy8cGEsYZ+Wft8fZ015LscL+viOSy4ONeNv5O+i2b/em7G0pp5nswrZhUBAE7XuQ8uqU86y2bc+VqtGyqK6ZTflq4xZ8qv8l0Iyf0rhdkzbtDQ4FOsOCy4OqffmZAUlkBzSOoaQrJW1GIRe6vdL91l1ykOFDqNuWNIpzFfdcpSF4xI+IK5z+LPzv5qgosafvHRPMdVpxw+U47EjbB5nsLAXD3noDK4tButZSQtdfWtEmgLOf+d6I2YIFX5A3wAANTCuQ8uSls/tjbLv1Sr04Kz297tKZ1OrLNnKrSIVMOd9nzcNY2cMq6XnxMcqTwF+yjaDeaUo+T5jmttR6+zceznAQDgSxBcDqFjPyavNXk+vx/L7EmgofurryU0saqzfPolu14YGOx087Q/OPH6SAAA2ILgcojM7r4Eex+Jr741320SamySpbnyLqWvoWfqnfguRPJl8Tc0ycxQt6ebBwCAbxnBBQAAWMPa4JJM/VX+bWqubDsAAPh2WRtcaHEBAOD8IbgAAABrEFzOGJ32vKbTlA/4yB0AAOcZweWMCcVXnI/hfe3p1gAA2IDgcsZkNvclvZDyfDvGZom3e5KePv2FFzPb+zJ5V1eyPtmXe2MvNmR5IfclYgDA2UNwwak6bP2mWtIlE/rqdWmCymsrVcv3Y6riEgcAgLPhXAeX6PQbiQ6NmX9hx2V+fV9auuLOGkCZ+PX8MbomT9/DjNl+XcJmX+qhfurf2xoy835fgldy6xklhq7L6FxG0tOFj9SNLmx4fuvqytGhWclmCl/BnV/VbXGnPKp4X63Kq/edMPcdfpZy9k/2XpVY2hx7aUAmzN/u+kvuM7V0jTvXH+4y+97nFlMsLsva61nPvYo/zDeZ0ecZE3/7Ten4rsn5e1Cfa9H7XMX3aTEmR/olu+ld4+kw7rsM3TDvvz5k/u537pVJxPLH6LsaHnrguXfsxUdJ3DHl2cndS/8f6Xm+7/qlp12vMyYxLe/6yYIQAKC2znVwWd7ck5a7GRmMNklLc0ySD03FdeNnz7+4A7fTMtjeJMuLKUn+siF17eOe/fPbukjjmCTvdMvy6oqMvlwRX0O3p5WhtNXBWZFaF0MsWu/IXcMotbohvkvximshnbS87n0TP4ZlxpTV1zgmkz+EJbn6TnxtpqL/vMiku4J0+uFN55l6EroSdNgEikIlri0TgYam/DGd0yvS16DLI+SOcdcw0vJO3mhy/l7TNY2KVsROmmf2N8YkMz3g7M8Y0Xvm/NfVd9W4ay6NvtqQnvqr5u/Z3NpJJWsw5RebNOEssanPN+BZVFPXpdLzfDdmJXVXr/O5vAySBoAz5VwHF6UVmlbAa3O5oKAV8lI8V9Hr+kAhXR+oaLXl0df7MtgYMX+nnd+dj/fMb60Qc7/daxw3uLjc1aYr7XOv9aXlLV49uvg+pff0m/BTXF4NB77ep7I81Z/fpvdNjeh1c7+1qyakXTVF93bLe1BX0X1tqdJz0icfiHxUV5Eu31Cn6zqZd+WPPpfk7crrO9FVBABnm9XB5Q+Ts/Jfb/92pNJzi2nFOtqmFWv5oM6+hX0J1zfJzNy48dwx/OS5qaCv5yvolvF3MtGl5+u/znPnnXZw+dLyVhNc3L8nopH8NVTgxs+eZyit4L8kuGi3VmAw5ay5FO26Kuk5c+5O4T0ex1HBxTlm0ZT7QreMfqdBs/z9qdLnAgCcLVYHl9//8c/yp7+8OFLpucXyXQifysdVaBAI1uv4jNy4Cdeojn1YzVWQwTtvZCbqrZhPO7h8aXmPE1zccR7FisfplFbwXxJcXOkPezL6MCV1lwYkfMEcu1h9V5GrmuCirU91FyLS19gq2U3vmB1X6XMBAM4Wq4NLrbqKDgoCWtF11kcku63TbMvPdc6Pr0jskvf83yq4HFXeaoKL2y2UvlPoBqqktII/SXBxaQuM79qszA+WH59eP3ya+FHBRcfTBC7GZMk8o7byJHr1HuXXKn0uAMDZQnA5JAg4FXr7zzLzYzhfYaZMBZpdzOSPGc1oK0dEtj6P00i8N+dcvOkNLhpuPt9Dg0FPYsUEl3DFcHKS4HJUeasJLnpc9NmehBrCspXJhRAtc+rlipR2h1UVXMyz3//elHdXzzfX2ikanLtpyvxkNj9gN72j5YhL+p43NC3p/cxz+eqbJDVSeWyKjpcJ6/3f51prtnZ0e+66TpeUKe9MNCQaVmbMfX2Ntzxjdlw+E2rmB/W4z+UsKi8A4Ld3roOLVr5aGboqhQWtXOsujUvgQpPUBSMSvKAzaQakuFJsGUmb81vFHwxJtLlVfNdueVtYtKJsHpNgsFUC5hoTI1dNBT3uuZ9W/D5T8RaXRxWHg5OWt9rgojqn3onPhJdAc8j8NySDl0P57jG3LNUEl+S2tzy58Tm5IJX4Zc/sG3PGuATaws47jF3T2UuFYKiW9X7ds7n38XkgcikNVy130lJnrhFoC0mwoVWy6dyH7/oWPkpfo1630D3UN/dROsxzZd8/8lxn8q3+vxqQQKN5x+acRK+5ToWWGQDAb+NcB5fj0KnIh02P1em0W+u5FonSriKlFatO283ufJ1K8KjyVsOdol06tfhLaHnc91PKnYp82LvR97e1fvD+/LV2dK0n77TrL7G8bsq7Wbm8AIDfDsHlFFQKLgAA4OQILqeA4AIAwOkguAAAAGsQXAAAgDWsDS5//5+PjtLtAADg22VtcAEAAOcPwQUAAFiD4AIAAKxBcAEAANYguAAAAGsQXAAAgDUILgAAwBoEFwAAYA2CCwAAsAbBBQAAWIPgAgAArEFwAQAA1iC4AAAAaxBcAACANQguAADAGgQXAABgDYILAACwBsEFAABYg+ACAACsQXABAADWILgAAABrEFwAAIA1CC4AAMAaBBcAAGANggsAALAGwQUAAFiD4AIAAKxBcAEAANYguAAAAGsQXAAAgDUILgAAwBoEFwAAYA2CCwAAsAbBBQAAWIPgAgAArEFwAQAA1iC4AAAAaxBcAACANQguAADAGgQXAABgDYILAACwBsEFAABYg+ACAACsQXABAADWILgAAABrEFwAAIA1CC4AAMAaBBcAAGANggsAALAGwQUAAFiD4AIAAKxBcAEAANYguAAAAGsQXAAAgDUILgAAwBoEFwAAYA2CCwAAsAbBBQAAWIPgAgAArEFwAQAA1iC4AAAAaxBcAACANQguAADAGgQXAABgDYILAACwBsEFAABYg+ACAACsQXABAADWILgAAABrEFwAAIA1CC4AAMAaBBcAAGANggsAALAGwQUAAFiD4AIAAKxBcAEAANYguAAAAGsQXAAAgDUILgAAwBoEFwAAYA2CCwAAsAbBBQAAWIPgAgAArEFwAQAA1iC4AAAAaxBcAACANQguAADAGgQXAABgDYILAACwBsEFAABYg+ACAACsQXABAADWILgAAABrEFwAAIA1CC4AAMAaBBcAAGANggsAALAGwQUAAFiD4AIAAKxBcAEAANYguAAAAGsQXAAAgDUILgAAwBoEFwAAYA2CCwAAsAbBBQAAWON32//3DwEAALDB7/539x8CAABgg/8HW2uj8DIQH+sAAAAASUVORK5CYII=>
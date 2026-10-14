# SDD Task Analyser

Biblioteca Python que transforma uma lista de tarefas em indicadores de produtividade: **tempo médio de conclusão**, **taxa de atraso** e **quantidade de tarefas**, no geral e por prioridade (`baixa`, `média`, `alta`).

O projeto segue **Spec-Driven Development**: a especificação em `specs/task_analyser_spec.md` é a fonte de verdade, e `CONTEXT_RULES.md` consolida as regras que o assistente de IA deve respeitar ao gerar código.

## Estrutura do projeto

```md
sdd-task-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml
├── specs/
│   └── task_analyser_spec.md
├── src/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── exceptions.py
│   └── models.py
├── tests/
│   ├── conftest.py
│   └── test_harness.py
├── .gitignore
├── CONTEXT_RULES.md
├── README.md
└── requirements.txt
```

## Como executar os testes

```bash
pip install -r requirements.txt
pytest
```

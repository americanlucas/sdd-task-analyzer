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
├── .venv/                # ambiente virtual local (não versionado)
├── .gitignore
├── CONTEXT_RULES.md
├── README.md
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Como executar os testes

Requer Python 3.11+. As dependências ficam isoladas em um ambiente virtual (`.venv/`, ignorado pelo git).

### 1. Criar o ambiente virtual (apenas na primeira vez)

```powershell
py -3.13 -m venv .venv
```

### 2. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

> Se o PowerShell bloquear a execução do script, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
> No Linux/macOS use `source .venv/bin/activate`.

### 3. Instalar as dependências

```powershell
pip install -r requirements.txt
```

### 4. Rodar os testes

```powershell
pytest
```

Sem ativar o ambiente, também é possível chamar o pytest direto pelo interpretador do venv:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

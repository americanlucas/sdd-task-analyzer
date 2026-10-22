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
├── .dockerignore
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

## Executar com Docker

Alternativa ao venv: roda a suíte em um contêiner com Python 3.13, sem instalar nada na máquina. Requer Docker (no Windows, o Docker Desktop precisa estar em execução).

```powershell
docker compose run --rm --build tests
```

- `Dockerfile`: parte de `python:3.13-slim`, instala o `requirements.txt`, copia `src/` e `tests/` e executa `pytest` por padrão.
- `docker-compose.yml`: serviço `tests` que monta `src/` e `tests/` como volumes. Ao editar o código, basta rodar o comando de novo, sem reconstruir a imagem (o `--build` só é necessário se o `requirements.txt` mudar).
- `.dockerignore`: mantém `.git`, `.venv` e caches fora da imagem.

Para construir e rodar a imagem diretamente, sem o compose:

```powershell
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

## CI (GitHub Actions)

O workflow `.github/workflows/ci.yml` roda a cada `push` e `pull_request`, em `ubuntu-24.04`, com uma matriz de Python **3.11** e **3.13** (`fail-fast` desligado, então uma versão não cancela a outra). Os passos espelham a execução local:

1. Checkout do repositório.
2. Configuração do Python, com cache do pip a partir do `requirements.txt`.
3. Criação do `.venv` e inclusão do `bin` dele no `PATH` do job.
4. `pip install -r requirements.txt`.
5. `pytest`.

Qualquer teste que falhe reprova o job. Conforme a homologação da spec (seção 10.1), o código só deve ser aprovado com 100% dos cenários passando. O CI não constrói a imagem Docker: o contêiner é para uso local.

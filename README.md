# TaskMaster API

API REST para gerenciamento de tarefas, desenvolvida com Python e FastAPI. O projeto oferece operações CRUD, validação de dados e persistência local em SQLite.

## Recursos

- Criar, listar, consultar, atualizar e excluir tarefas.
- Validar os dados de entrada e retornar erros HTTP apropriados.
- Salvar os dados em SQLite, preservando as tarefas após reiniciar o servidor.
- Explorar e testar os endpoints pela documentação interativa do FastAPI.
- Executar testes automatizados com o módulo `unittest` da biblioteca padrão do Python.

## Tecnologias

- Python 3.10+
- FastAPI
- Uvicorn
- SQLite (`sqlite3`, incluído no Python)
- `unittest`

## Requisitos

- Python 3.10 ou mais recente
- Git (opcional para executar; necessário para versionar o projeto)

## Instalação no Windows

No terminal do VS Code, na pasta do projeto, crie e ative um ambiente virtual e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação, libere scripts apenas na janela atual e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Executar a API

Com o ambiente virtual ativo:

```powershell
python -m uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Documentação interativa: <http://127.0.0.1:8000/docs>
- Verificação de saúde: <http://127.0.0.1:8000/health>

O arquivo `taskmaster.db` é criado automaticamente na pasta do projeto quando a API inicia. Não é preciso instalar um servidor de banco de dados.

## Endpoints

| Método | Rota | Descrição | Respostas principais |
|---|---|---|---|
| `GET` | `/health` | Confirma que a API está ativa | `200` |
| `POST` | `/tasks` | Cria uma tarefa | `201`, `422` |
| `GET` | `/tasks` | Lista todas as tarefas | `200` |
| `GET` | `/tasks/{task_id}` | Consulta uma tarefa pelo ID | `200`, `404` |
| `PUT` | `/tasks/{task_id}` | Substitui os campos editáveis da tarefa | `200`, `404`, `422` |
| `DELETE` | `/tasks/{task_id}` | Exclui uma tarefa | `204`, `404` |

### Criar uma tarefa

Envie um `POST` para `/tasks` com:

```json
{
  "title": "Estudar FastAPI",
  "description": "Criar minha primeira API"
}
```

O título deve ter entre 1 e 100 caracteres. A descrição é opcional na criação e aceita até 500 caracteres. A resposta inclui o ID gerado e `completed: false`.

### Atualizar uma tarefa

Envie um `PUT` para `/tasks/{task_id}` com todos os campos editáveis:

```json
{
  "title": "Estudar FastAPI",
  "description": "Revisar os endpoints CRUD",
  "completed": true
}
```

Como é um `PUT`, envie `title`, `description` e `completed` na atualização. Use `/docs` para enviar essas requisições e ver as respostas no navegador.

## Executar os testes

Com o ambiente virtual ativo, execute:

```powershell
python -m unittest discover -s tests -v
```

Os testes usam um banco temporário para não alterar o arquivo de dados local.

## Estrutura do projeto

```text
app/
  database.py       # Conexão SQLite e operações de persistência
  main.py           # Aplicação FastAPI, modelos e endpoints
tests/
  test_tasks.py     # Testes automatizados das operações principais
requirements.txt    # Dependências da aplicação
taskmaster.db      # Banco local criado durante a execução (ignorado pelo Git)
```

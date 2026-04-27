# 🤖 Media Analyst Agent

Agente de IA Autônomo que atua como **Analista Júnior de Mídia**, respondendo perguntas em linguagem natural sobre performance de canais de tráfego com dados reais do BigQuery.

## Arquitetura

O agente usa o padrão **ReAct (Reason + Act)** via LangGraph:

1. Usuário faz uma pergunta em linguagem natural
2. FastAPI recebe via `POST /api/v1/query`
3. LangGraph passa para o LLM (GPT-4o)
4. O LLM decide qual **tool** chamar com base na pergunta
5. A tool executa uma query SQL parametrizada no BigQuery
6. O resultado volta para o LLM, que formula a resposta final

### Tools disponíveis

| Tool                               | Quando é usada                            |
| ---------------------------------- | ----------------------------------------- |
| `get_traffic_volume_by_source`     | Volume de usuários de um canal específico |
| `get_all_channels_performance`     | Comparativo geral entre canais            |
| `get_revenue_by_channel_over_time` | Evolução de receita ao longo do tempo     |
| `get_top_converting_channels`      | Ranking por taxa de conversão             |

## Setup

### Pré-requisitos

- Python 3.10+
- Conta no Google Cloud com BigQuery habilitado
- Chave de API da OpenAI

### Credenciais GCP

Crie uma Service Account com o papel **BigQuery Job User**, baixe o JSON e configure no `.env`.

### Instalação

```bash
git clone https://github.com/seu-usuario/media-analyst-agent
cd media-analyst-agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edite o .env com suas chaves
```

### Rodando

```bash
uvicorn app.main:app --reload
```

Acesse `http://localhost:8000/docs` para a documentação interativa.

## Exemplos de uso

```bash
# Volume de um canal
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Como foi o volume de usuários vindos de Search no último mês?"}'

# Comparativo geral
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual dos canais tem a melhor performance?"}'
```

## Estrutura do projeto

```
media-agent/
├── app/
│   ├── main.py                 # Entrypoint FastAPI
│   ├── api/routes.py           # Endpoints REST
│   ├── agent/media_agent.py    # LangGraph ReAct Agent
│   ├── tools/bigquery_tools.py # 4 tools com @tool decorator
│   ├── models/schemas.py       # Pydantic models
│   └── core/
│       ├── config.py           # Settings com pydantic-settings
│       └── bigquery_client.py  # Cliente BQ parametrizado
└── tests/
```

## Segurança

- Queries 100% parametrizadas via `bigquery.ScalarQueryParameter`

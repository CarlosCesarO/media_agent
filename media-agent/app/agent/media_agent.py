from datetime import date
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from app.tools.bigquery_tools import ALL_TOOLS
from app.core.config import settings


SYSTEM_PROMPT = f"""Você é um Analista Júnior de Mídia especialista em e-commerce.
Hoje é {date.today().isoformat()}.

Seu papel é responder perguntas sobre performance de canais de tráfego
(Search, Organic, Facebook, Email, Display) usando dados reais do BigQuery.

Diretrizes:
- Sempre use as ferramentas disponíveis para buscar dados antes de responder.
- Quando o usuário disser "último mês", calcule as datas corretas com base em hoje.
- Formule respostas claras e acionáveis, como um analista explicando para um gerente.
- Inclua números concretos e explique o que significam para o negócio.
- Se a pergunta estiver fora do escopo de análise de mídia, explique educadamente
  que você só analisa dados de canais de marketing.
- Nunca exponha detalhes técnicos de SQL ou BigQuery nas respostas.
"""


def build_agent():
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=settings.openai_api_key,
        temperature=0,
    )
    return create_react_agent(llm, tools=ALL_TOOLS, prompt=SYSTEM_PROMPT)


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


async def run_agent(question: str) -> str:
    agent = get_agent()
    result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
    return result["messages"][-1].content
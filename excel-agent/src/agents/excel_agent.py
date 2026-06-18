from __future__ import annotations
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from .tools import TOOLS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um assistente especializado em análise de dados de planilhas Excel.
Você tem acesso a ferramentas para consultar registros, filtrar dados e verificar alterações.

Responda sempre em português do Brasil de forma clara e objetiva.
Use as ferramentas disponíveis para obter os dados necessários antes de responder.
Se não encontrar dados, informe claramente ao usuário."""


class ExcelAgent:
    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        llm = ChatAnthropic(model=model, temperature=0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        agent = create_tool_calling_agent(llm, TOOLS, prompt)
        self._executor = AgentExecutor(
            agent=agent,
            tools=TOOLS,
            verbose=False,
            max_iterations=5,
            return_intermediate_steps=False,
        )

    async def ask(self, pergunta: str) -> str:
        try:
            result = await self._executor.ainvoke({"input": pergunta})
            return result.get("output", "Não foi possível obter uma resposta.")
        except Exception as e:
            logger.exception(f"Agent error: {e}")
            return f"Erro ao processar a pergunta: {str(e)}"

from __future__ import annotations
import logging
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
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
        self._agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)

    async def ask(self, pergunta: str) -> str:
        try:
            result = await self._agent.ainvoke(
                {"messages": [HumanMessage(content=pergunta)]}
            )
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content and not getattr(msg, "tool_calls", None):
                    content = msg.content
                    if isinstance(content, list):
                        return " ".join(
                            block.get("text", "") for block in content
                            if isinstance(block, dict) and block.get("type") == "text"
                        )
                    return str(content)
            return "Não foi possível obter uma resposta."
        except Exception as e:
            logger.exception(f"Agent error: {e}")
            return f"Erro ao processar a pergunta: {str(e)}"

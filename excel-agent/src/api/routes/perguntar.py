from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...agents.excel_agent import ExcelAgent

router = APIRouter()
_agent: ExcelAgent | None = None


def init_router(agent: ExcelAgent) -> None:
    global _agent
    _agent = agent


class PerguntaRequest(BaseModel):
    pergunta: str


class PerguntaResponse(BaseModel):
    resposta: str


@router.post("/perguntar", response_model=PerguntaResponse)
async def perguntar(request: PerguntaRequest):
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not ready")
    resposta = await _agent.ask(request.pergunta)
    return PerguntaResponse(resposta=resposta)

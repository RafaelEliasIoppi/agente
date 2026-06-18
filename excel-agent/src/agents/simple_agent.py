from __future__ import annotations
import json
import re
from ..repositories.snapshot_repo import SnapshotRepository
from ..repositories.history_repo import HistoryRepository


class SimpleAgent:
    """Agente por regras — funciona sem API key Anthropic."""

    def __init__(self, snapshot_repo: SnapshotRepository, history_repo: HistoryRepository) -> None:
        self._snap = snapshot_repo
        self._hist = history_repo

    async def ask(self, pergunta: str) -> str:
        p = pergunta.lower()
        snap = self._snap.load()
        registros = snap.registros if snap else []
        dados = [r.dados for r in registros]

        # Quantos registros
        if any(w in p for w in ["quantos", "total", "quantidade"]):
            return f"Existem {len(dados)} registros na planilha."

        # Alterações hoje
        if "hoje" in p and any(w in p for w in ["alter", "mudou", "mudança"]):
            events = self._hist.load_today()
            if not events:
                return "Nenhuma alteração registrada hoje."
            return f"Foram encontradas {len(events)} alteração(ões) hoje."

        # Busca por status
        for status_kw in ["pendente", "concluído", "concluido", "ativo", "inativo", "aguardando"]:
            if status_kw in p:
                resultado = [
                    r for r in dados
                    if any(status_kw in str(v).lower() for v in r.values())
                ]
                if not resultado:
                    return f"Nenhum registro com status '{status_kw}'."
                return (
                    f"{len(resultado)} registro(s) com '{status_kw}':\n" +
                    json.dumps(resultado[:10], ensure_ascii=False, default=str, indent=2)
                )

        # Busca por nome
        match = re.search(r"(de|do|da|para|sobre)\s+([A-ZÁÉÍÓÚÀÂÊÔÃÕÇ][a-záéíóúàâêôãõç]+)", pergunta)
        if match:
            nome = match.group(2).lower()
            resultado = [r for r in dados if any(nome in str(v).lower() for v in r.values())]
            if resultado:
                return (
                    f"{len(resultado)} registro(s) encontrado(s) para '{match.group(2)}':\n" +
                    json.dumps(resultado[:10], ensure_ascii=False, default=str, indent=2)
                )

        # Listar tudo
        if any(w in p for w in ["listar", "mostrar", "exibir", "todos", "todas"]):
            if not dados:
                return "Nenhum registro disponível."
            return (
                f"{len(dados)} registros (exibindo primeiros 5):\n" +
                json.dumps(dados[:5], ensure_ascii=False, default=str, indent=2)
            )

        # Colunas disponíveis
        if any(w in p for w in ["coluna", "campo", "campo"]):
            if dados:
                colunas = list(dados[0].keys())
                return f"Colunas disponíveis: {', '.join(colunas)}"

        if not dados:
            return "Nenhum dado carregado ainda. Aguarde o próximo ciclo de monitoramento."

        return (
            f"Entendi sua pergunta mas não consigo processá-la sem a API do Claude.\n"
            f"Configure ANTHROPIC_API_KEY no .env para respostas inteligentes.\n\n"
            f"Dados disponíveis: {len(dados)} registros com colunas: "
            f"{', '.join(dados[0].keys()) if dados else 'nenhuma'}"
        )

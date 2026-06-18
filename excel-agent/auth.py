"""
Script de autenticação inicial — Device Code Flow.

Execute UMA VEZ antes de iniciar o servidor:
    python auth.py

Você será direcionado para fazer login no browser com sua conta Microsoft.
O token ficará salvo em data/token_cache.json e será renovado automaticamente.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import settings
from src.graph.client import GraphClient


def main() -> None:
    print("Iniciando autenticação Microsoft 365 (Device Code Flow)...")
    print(f"Tenant:     {settings.azure_tenant_id}")
    print(f"Client ID:  {settings.azure_client_id}")
    print(f"Cache path: {settings.token_cache_path}\n")

    client = GraphClient(
        client_id=settings.azure_client_id,
        tenant_id=settings.azure_tenant_id,
        token_cache_path=settings.token_cache_path,
    )

    # Força a autenticação agora (vai exibir o código para o browser)
    token = client._acquire_token_sync()

    print("\n✓ Autenticação concluída com sucesso!")
    print(f"✓ Token salvo em: {settings.token_cache_path}")
    print("\nAgora você pode iniciar o servidor normalmente:")
    print("  uvicorn src.api.main:app --port 8000")


if __name__ == "__main__":
    main()

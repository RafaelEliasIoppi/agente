#!/bin/bash
set -e

VERDE="\033[0;32m"
AMARELO="\033[1;33m"
VERMELHO="\033[0;31m"
AZUL="\033[0;34m"
RESET="\033[0m"

echo ""
echo -e "${AZUL}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${AZUL}║        Excel Agent — UrgenciaRenal 2026      ║${RESET}"
echo -e "${AZUL}╚══════════════════════════════════════════════╝${RESET}"
echo ""

# ── Verifica Python ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${VERMELHO}✗ Python 3 não encontrado. Instale Python 3.12+${RESET}"
    exit 1
fi
echo -e "${VERDE}✓ Python: $(python3 --version)${RESET}"

# ── Verifica .env ──────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo -e "${AMARELO}⚠  Arquivo .env não encontrado. Criando a partir do exemplo...${RESET}"
    cp .env.example .env
    echo -e "${AMARELO}   Edite o .env com suas credenciais antes de continuar.${RESET}"
fi

# ── Instala dependências ───────────────────────────────────────
echo ""
echo -e "${AZUL}► Verificando dependências...${RESET}"
if ! python3 -c "import fastapi" &>/dev/null; then
    echo -e "${AMARELO}  Instalando requirements.txt...${RESET}"
    pip install -r requirements.txt -q
    echo -e "${VERDE}✓ Dependências instaladas${RESET}"
else
    echo -e "${VERDE}✓ Dependências já instaladas${RESET}"
fi

# ── Cria pastas de dados ───────────────────────────────────────
mkdir -p data/snapshots data/history data/logs demo_data

# ── Verifica planilha local ────────────────────────────────────
PLANILHA="demo_data/UrgenciaRenal - 2026.xlsx"
if [ ! -f "$PLANILHA" ]; then
    echo ""
    echo -e "${AMARELO}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${AMARELO}║  ATENÇÃO: Planilha não encontrada!                          ║${RESET}"
    echo -e "${AMARELO}║                                                              ║${RESET}"
    echo -e "${AMARELO}║  1. Abra o link abaixo no navegador:                        ║${RESET}"
    echo -e "${AMARELO}║     https://rsgovbr-my.sharepoint.com (faça login)          ║${RESET}"
    echo -e "${AMARELO}║                                                              ║${RESET}"
    echo -e "${AMARELO}║  2. Baixe o arquivo: UrgenciaRenal - 2026.xlsx              ║${RESET}"
    echo -e "${AMARELO}║                                                              ║${RESET}"
    echo -e "${AMARELO}║  3. Salve em:                                               ║${RESET}"
    echo -e "${AMARELO}║     excel-agent/demo_data/UrgenciaRenal - 2026.xlsx         ║${RESET}"
    echo -e "${AMARELO}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
    read -p "Pressione ENTER após salvar o arquivo para continuar (ou Ctrl+C para cancelar)..."
fi

# ── Autenticação Azure (modo SharePoint) ──────────────────────
if grep -q "^AZURE_CLIENT_ID=.\+" .env 2>/dev/null && ! grep -q "^DEMO_MODE=true" .env 2>/dev/null; then
    if [ ! -f "data/token_cache.json" ]; then
        echo ""
        echo -e "${AZUL}► Autenticação Microsoft 365 necessária...${RESET}"
        python3 auth.py
    else
        echo -e "${VERDE}✓ Token Microsoft encontrado${RESET}"
    fi
fi

# ── Porta ──────────────────────────────────────────────────────
PORTA=${PORT:-8000}

# ── Inicia servidor ────────────────────────────────────────────
echo ""
echo -e "${VERDE}► Iniciando servidor na porta ${PORTA}...${RESET}"
echo ""
echo -e "${AZUL}  API disponível em:${RESET}"
echo -e "  ${VERDE}http://localhost:${PORTA}/status${RESET}          → Status do serviço"
echo -e "  ${VERDE}http://localhost:${PORTA}/dados${RESET}           → Dados da planilha"
echo -e "  ${VERDE}http://localhost:${PORTA}/alteracoes${RESET}      → Histórico de alterações"
echo -e "  ${VERDE}http://localhost:${PORTA}/alteracoes/hoje${RESET} → Alterações de hoje"
echo -e "  ${VERDE}http://localhost:${PORTA}/docs${RESET}            → Documentação interativa (Swagger)"
echo ""
echo -e "${AZUL}  Monitoramento: a cada 60s verifica alterações na planilha${RESET}"
echo -e "${AZUL}  Pressione Ctrl+C para encerrar${RESET}"
echo ""

python3 -m uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port "$PORTA" \
    --log-level info

# Excel Agent — Monitoramento de Planilha Excel Online

Serviço Python autônomo que monitora planilhas Excel hospedadas no SharePoint/OneDrive via Microsoft Graph API e permite consultas em linguagem natural via Claude (Anthropic).

## Funcionalidades

- Monitoramento automático a cada 5 minutos
- Detecção de novas linhas, exclusões e alterações por campo
- API REST para consulta dos dados e histórico
- Agente de linguagem natural (Claude) para perguntas sobre os dados
- Notificações via Console e E-mail SMTP

## Requisitos

- Python 3.12+
- Conta Microsoft 365 com acesso à planilha
- Azure App Registration com permissões delegadas para Microsoft Graph
- API Key da Anthropic

## Configuração Rápida

### 1. Clone e configure o ambiente

```bash
cd excel-agent
cp .env.example .env
# Edite o .env com suas credenciais
pip install -r requirements.txt
```

### 2. Configure o Azure App Registration

No portal Azure (portal.azure.com):
1. Acesse **Azure Active Directory → App registrations → New registration**
2. Tipo de conta: *Accounts in this organizational directory only*
3. Em **API permissions**, adicione as permissões delegadas do Microsoft Graph:
   - `Files.Read.All`
   - `Sites.Read.All`
4. Em **Authentication**, habilite **Allow public client flows** (necessário para ROPC)
5. Copie o **Application (client) ID** e o **Directory (tenant) ID** para o `.env`

### 3. Obtenha os IDs do SharePoint

```bash
# Liste drives disponíveis (após obter token)
curl -H "Authorization: Bearer <token>" \
  "https://graph.microsoft.com/v1.0/me/drives"

# Liste itens do drive para encontrar o workbook
curl -H "Authorization: Bearer <token>" \
  "https://graph.microsoft.com/v1.0/drives/{drive-id}/root/children"
```

### 4. Execute

```bash
# Desenvolvimento
uvicorn src.api.main:app --reload --port 8000

# Docker
docker-compose up --build
```

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /status | Status do serviço e último ciclo |
| GET | /dados | Todos os registros do snapshot atual |
| GET | /alteracoes | Histórico completo de alterações |
| GET | /alteracoes/hoje | Alterações do dia |
| GET /registro/{id} | Registro por ID |
| POST | /perguntar | Consulta em linguagem natural |

### Exemplo — Pergunta em linguagem natural

```bash
curl -X POST http://localhost:8000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Quais registros mudaram hoje?"}'
```

Exemplos de perguntas suportadas:
- *"Quantos registros existem?"*
- *"Mostre todos os registros de Rafael"*
- *"Quais estão com status Pendente?"*
- *"Existe algum processo concluído hoje?"*
- *"Busque o registro com CPF 123.456.789-00"*

## Estrutura do Projeto

```
src/
  config/       Configurações via Pydantic BaseSettings
  graph/        Cliente Microsoft Graph API (MSAL ROPC + httpx)
  models/       Modelos Pydantic (Record, ChangeEvent, Snapshot)
  repositories/ Persistência JSON (snapshot + histórico)
  services/     Lógica de negócio (diff, monitor)
  scheduler/    APScheduler para execução periódica
  agents/       Agente LangChain + Claude
  api/          FastAPI (endpoints REST)
  notifications/Notificadores (Console, E-mail)
  storage/      I/O de arquivos JSON atômico
  logs/         Configuração de logging estruturado
data/
  snapshots/    snapshot_atual.json
  history/      historico_alteracoes.json
  logs/         app.log
```

## Testes

```bash
pytest tests/ -v
```

## Variáveis de Ambiente

Veja [.env.example](.env.example) para a lista completa.

# iCREATE Automation Engine - Global Production Standards

**Compliance:** 12-Factor App, MCP 2024-11-05, JSON-RPC 2.0, OpenAPI 3.1, RFC 6455 (WS), OpenTelemetry, Prometheus, ISO 27001 logging, GDPR-ready.

## Architecture
```
Client (Claude/Cursor/n8n/Web) -> [Connector Layer: Stdio/WS/TCP/SSE/gRPC]
                                  -> [Security: JWT/APIKey/OAuth2 + RateLimiter]
                                  -> [MCP Server: tools/list, tools/call, resources, prompts]
                                  -> [Engine Core: DAG + Executors + StateStore (Postgres/Redis)]
                                  -> [Observability: JSON Logs + Prometheus + OTel Tracing]
```

## Quick Start (Prod)
```bash
cp .env.example .env
docker-compose up --build -d
curl http://localhost:8000/health/ready
curl http://localhost:8000/docs # OpenAPI
```

## MCP Clients
Claude Desktop config:
```json
{"mcpServers":{"pyautoforge":{"command":"docker","args":["exec","-i","icreate_automation_engine-api-1","python","-m","pyautoforge.connectors.stdio"]}}}
```

WebSocket prod: `wss://your-domain.com/mcp` with header `Authorization: Bearer <JWT>`

## Standards Implemented
- **Code:** ruff lint, mypy strict, 100% type hints, semver 2.0.0
- **Config:** Pydantic Settings from env (12-factor)
- **Security:** JWT + API Key + OAuth2 ready, non-root Docker, secrets via env, rate limit Redis, input validation Pydantic
- **Reliability:** Health /live /ready, graceful shutdown, circuit breaker, exponential backoff, idempotency keys
- **Observability:** JSON structured logs, Prometheus metrics at :9001/metrics, OTel traces, correlation-id
- **Scalability:** Horizontal via Redis queue, Postgres state, K8s HPA
- **Compliance:** Audit logs, GDPR data retention, ISO 27001 log retention

## K8s Deploy
```bash
kubectl apply -f k8s/
```

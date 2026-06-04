# SCADA LLM Security Middleware

Academic, production-oriented middleware for protecting language model requests and responses in SCADA and electrical-grid contexts.

The service sits inside a private `10.x.x.x` network between a web/API client, a RoBERTa classifier API, and a Mistral API. It classifies prompts, applies security rules, blocks risky input or output, and records audit events.

## Table of Contents

1. [Overview](#1-overview)
2. [Documentation](#2-documentation)
3. [Project Structure](#3-project-structure)
4. [Configuration](#4-configuration)
5. [Local Development](#5-local-development)
6. [External Services](#6-external-services)
7. [Main Endpoints](#7-main-endpoints)
8. [Testing](#8-testing)
9. [Security](#9-security)

## 1. Overview

This project provides a FastAPI security gateway for LLM usage in industrial-control scenarios.

This repository runs only as middleware. It consumes:

- RoBERTa classifier API through `ROBERTA_URL` and `ROBERTA_ENDPOINT`.
- Mistral API through `MISTRAL_URL` and `MISTRAL_ENDPOINT`.

The middleware validates prompts, requests classification, applies rule-based controls, sends allowed prompts to Mistral, validates generated output, and records audit logs.

## 2. Documentation

- [API Reference](docs/API.md): endpoints, examples, and common errors.
- [Architecture](docs/ARCHITECTURE.md): middleware components and request flow.
- [Model Card](docs/MODEL_CARD.md): intended use, limitations, and expected RoBERTa classifier behavior.
- [Security Policy](SECURITY.md): vulnerability reporting, secret handling, and deployment notes.

`SECURITY.md` stays at the repository root because platforms like GitHub detect it automatically. Longer technical documents live in `docs/`.

## 3. Project Structure

```text
project/
├── app/
│   ├── api/
│   ├── core/
│   ├── middleware/
│   ├── rules/
│   ├── schemas/
│   ├── security/
│   ├── services/
│   ├── utils/
│   └── web/
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── MODEL_CARD.md
├── models/
├── tests/
├── .env.example
├── main.py
├── README.md
├── run.ps1
├── SECURITY.md
└── requirements.txt
```

## 4. Configuration

Copy `.env.example` to `.env` and adjust the internal service URLs.

```env
ROBERTA_URL=http://10.x.x.x:8001
ROBERTA_ENDPOINT=/prompt

MISTRAL_URL=http://10.x.x.x:8002
MISTRAL_ENDPOINT=/chat

REQUEST_TIMEOUT_SECONDS=30
```

### 4.1 Configuration Notes

- `ROBERTA_URL` points to the internal RoBERTa classifier API.
- `ROBERTA_ENDPOINT` points to the RoBERTa prompt classification endpoint.
- `MISTRAL_URL` points to the internal Mistral API host.
- `MISTRAL_ENDPOINT` points to the Mistral chat endpoint on that host.
- The Mistral service owns its local model selection.
- `REQUEST_TIMEOUT_SECONDS` controls backend service calls and the browser chat timeout.
- `.env` must not be committed.

## 5. Local Development

Start the PowerShell menu:

```powershell
.\run.ps1
```

Menu options:

```text
1. Start
2. Stop
```

The middleware starts at:

```text
http://127.0.0.1:8000
```

The web client is available at:

```text
http://127.0.0.1:8000/
```

## 6. External Services

### 6.1 RoBERTa Classifier API

```env
ROBERTA_URL=http://10.x.x.x:8001
ROBERTA_ENDPOINT=/prompt
```

Expected classifier endpoints:

- `GET /health`
- `POST /prompt`

### 6.2 Mistral API

```env
MISTRAL_URL=http://10.x.x.x:8002
MISTRAL_ENDPOINT=/chat
```

The middleware posts allowed prompts to `MISTRAL_URL + MISTRAL_ENDPOINT`.

## 7. Main Endpoints

- `GET /health`
- `GET /web/config`
- `POST /web/chat`
- `POST /api/chat`

See [docs/API.md](docs/API.md) for full request and response contracts.

## 8. Testing

```powershell
pytest
```

The test suite covers rule-based blocking, degraded classifier behavior, and middleware routing behavior.

## 9. Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting, secret handling, and deployment recommendations.

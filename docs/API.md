# API Reference

## 1. Purpose

This API is the middleware surface for internal clients in the private `10.x.x.x` network.

The middleware does not host RoBERTa or Mistral. It consumes both services as internal APIs:

- RoBERTa verifies and classifies every prompt first.
- Mistral receives only prompts that are not classified as malicious.
- Malicious prompts are rejected with `We are sorry we can't do that`.

## 2. Base URL

Middleware:

```text
http://127.0.0.1:8000
```

Production or lab deployments should expose the middleware only inside the trusted private network.

## 3. Network Access

There is no local `X-API-Key` requirement.

Access control is expected to be handled by:

- Private `10.x.x.x` network segmentation.
- Firewall rules.
- Host allowlists.
- Lab VPN or controlled routing.

## 4. Security Flow

```text
Client prompt
    |
    v
Middleware
    |
    v
RoBERTa verification/classification
    |
    |-- malicious     -> reject user request
    |
    '-- non-malicious -> forward to Mistral
                            |
                            v
                         return response
```

Blocked message:

```text
We are sorry we can't do that
```

## 5. Middleware Endpoints

### 5.1 Health

`GET /health`

Returns middleware dependency health.

Healthy response:

```json
{
  "status": "healthy",
  "roberta_loaded": true,
  "mistral_available": true
}
```

Degraded response:

```json
{
  "status": "degraded",
  "roberta_loaded": false,
  "mistral_available": false,
  "error": "RoBERTa API unavailable; Mistral API unavailable"
}
```

### 5.2 Web Config

`GET /web/config`

Returns safe runtime settings used by the browser client.

```json
{
  "request_timeout_seconds": 30.0
}
```

### 5.3 Internal Chat

`POST /api/chat`

Internal chat endpoint for trusted clients on the private network.

Headers:

```text
Content-Type: application/json
```

Request:

```json
{
  "prompt": "Explain IEC 61850 at a high level."
}
```

Allowed response:

```json
{
  "request_id": "uuid",
  "decision": "allowed",
  "classification": {
    "label": "safe",
    "score": 0.94
  },
  "triggered_rules": [],
  "response": "IEC 61850 is a communication standard..."
}
```

Blocked malicious prompt response:

```json
{
  "request_id": "uuid",
  "decision": "blocked_input",
  "classification": {
    "label": "malicious",
    "score": 0.98
  },
  "triggered_rules": [],
  "response": "We are sorry we can't do that"
}
```

Blocked by rule response:

```json
{
  "request_id": "uuid",
  "decision": "blocked_input",
  "classification": {
    "label": "suspicious",
    "score": 0.86
  },
  "triggered_rules": ["protocol-dnp3-control"],
  "response": "We are sorry we can't do that"
}
```

Blocked output response:

```json
{
  "request_id": "uuid",
  "decision": "blocked_output",
  "classification": {
    "label": "safe",
    "score": 0.91
  },
  "triggered_rules": ["unsafe-output-pattern"],
  "response": "We are sorry we can't do that"
}
```

Example:

```powershell
Invoke-RestMethod `
  -Method POST `
  -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" `
  -Body '{"prompt":"Explain what IEC 61850 is at a high level."}'
```

### 5.4 Web Chat

`POST /web/chat`

Browser chat endpoint used by `app/web/app.js`.

Request:

```json
{
  "prompt": "Explain Modbus at a high level."
}
```

Response shape is the same as `POST /api/chat`.

## 6. External Service Contracts

### 6.1 RoBERTa

The middleware sends every prompt to:

```text
ROBERTA_URL + ROBERTA_ENDPOINT
```

Current expected endpoint:

```env
ROBERTA_ENDPOINT=/prompt
```

Request sent by the middleware:

```json
{
  "text": "Explain Modbus at a high level.",
  "request_id": "uuid"
}
```

Expected response:

```json
{
  "label": "safe",
  "score": 0.94
}
```

Expected labels:

- `safe`
- `suspicious`
- `malicious`

### 6.2 Mistral

The middleware forwards only non-malicious prompts to:

```text
MISTRAL_URL + MISTRAL_ENDPOINT
```

Current expected endpoint:

```env
MISTRAL_ENDPOINT=/chat
```

Request sent by the middleware:

```json
{
  "prompt": "Explain Modbus at a high level."
}
```

The middleware accepts any of these response fields:

```json
{
  "response": "..."
}
```

```json
{
  "message": "..."
}
```

```json
{
  "text": "..."
}
```

## 7. Security Metrics

These metrics are security-focused. They are meant to describe blocking, classification, and policy behavior, not runtime performance.

### 7.1 Required Metrics

Track these from `ChatResponse` and audit records:

- Total chat requests.
- Allowed requests: `decision = allowed`.
- Blocked malicious prompts: `decision = blocked_input` and `classification.label = malicious`.
- Blocked suspicious or policy-matching prompts: `decision = blocked_input` with triggered rules.
- Blocked outputs: `decision = blocked_output`.
- RoBERTa label distribution: count of `safe`, `suspicious`, and `malicious`.
- High-confidence malicious detections: `classification.label = malicious` with score above the chosen review threshold.
- Triggered rule frequency by rule id.
- Dependency degradation events for RoBERTa and Mistral.

### 7.2 Useful Rates

Compute these over a fixed review window:

```text
malicious_prompt_rate = blocked_malicious_prompts / total_chat_requests
policy_block_rate = blocked_by_rules / total_chat_requests
allowed_rate = allowed_requests / total_chat_requests
blocked_output_rate = blocked_outputs / total_chat_requests
```

### 7.3 Review Signals

Prioritize manual review when:

- A single client host produces repeated malicious prompts.
- One rule id triggers unusually often.
- `classification.label` and triggered rules disagree frequently.
- RoBERTa or Mistral degradation causes repeated unavailable responses.

### 7.4 Not Security Metrics

Do not treat these as security metrics for this project:

- Latency.
- Throughput.
- CPU or memory usage.
- Token generation speed.

Those can be operational metrics, but they do not measure prompt safety or policy enforcement.

## 8. Common Errors

### 8.1 RoBERTa Unavailable

The middleware cannot reach the classifier configured by `ROBERTA_URL` and `ROBERTA_ENDPOINT`.

### 8.2 Mistral Unavailable

The middleware cannot reach the Mistral service configured by `MISTRAL_URL` and `MISTRAL_ENDPOINT`.

### 8.3 Timeout

Requests to backend services are limited by:

```env
REQUEST_TIMEOUT_SECONDS=30
```

The browser also uses this value through `GET /web/config`.

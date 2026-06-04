# Security Policy

## Scope

This project is a SCADA LLM security middleware. Security reports should focus on issues that affect:

- API key validation or authentication bypass.
- Prompt filtering, classification, or rule enforcement bypasses.
- Unsafe handling of requests, responses, audit logs, or environment variables.
- Exposure of secrets, internal service URLs, model paths, or sensitive logs.
- Denial of service risks in the FastAPI backend or web chat client.

## Reporting a Vulnerability

Do not open a public issue with exploit details, secrets, internal URLs, or payloads that could be reused against a real environment.

Report privately to the project maintainer with:

- A short description of the issue.
- Steps to reproduce.
- Affected endpoint, file, or component.
- Expected impact.
- Suggested fix, if known.

If this repository is used in an academic or lab environment, report the issue to the responsible instructor, maintainer, or deployment owner.

## Secrets and Environment Files

The real `.env` file must not be committed. Use `.env.example` as the public template.

Keep these values private:

- Internal `ROBERTA_URL`
- Internal `MISTRAL_URL`
- Any production model paths, hostnames, or network addresses

Rotate any internal service credential if one is later added and exposed in logs, screenshots, commits, demos, or shared machines.

## Deployment Notes

- Run the middleware behind a trusted network boundary or reverse proxy.
- Use HTTPS when exposing the service outside localhost or a lab-only network.
- Restrict access to `/api/chat` with network controls such as firewall rules, host allowlists, or lab VPN segmentation.
- Keep `REQUEST_TIMEOUT_SECONDS` reasonable to avoid long-running stuck requests.
- Review audit logs before sharing them, because they may contain prompts and generated responses.

## Supported Versions

This project currently supports the latest code in the main working branch only.

## Security Testing

Before deployment, verify:

- `/api/chat` is reachable only from the intended private network.
- Malicious or unsafe prompts are blocked by rules/classification.
- RoBERTa and Ollama outages return degraded or unavailable responses instead of leaking internals.
- `.env` is ignored by Git and `.env.example` contains only safe placeholder values.

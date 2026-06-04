# Model Card

## 1. Model

RoBERTa classifier for SCADA-related LLM prompt safety.

This repository does not host or train the classifier. The classifier is an internal service operated separately and consumed by the middleware through:

```env
ROBERTA_URL=http://10.x.x.x:8001
ROBERTA_ENDPOINT=/prompt
```

## 2. Purpose

The classifier verifies whether a user prompt is safe, suspicious, or malicious before the middleware sends anything to Mistral.

Its primary purpose is security filtering:

- Detect malicious prompts.
- Support policy decisions before LLM generation.
- Prevent unsafe prompts from reaching the Mistral service.
- Provide classification evidence for audit review.

## 3. Intended Use

Use this classifier as the first security step in the middleware flow:

1. User sends a prompt to the middleware.
2. Middleware sends the prompt to RoBERTa.
3. RoBERTa returns a safety label and confidence score.
4. If the prompt is malicious, the middleware rejects it.
5. If the prompt is not malicious, the middleware may forward it to Mistral.

Blocked malicious prompts return:

```text
We are sorry we can't do that
```

## 4. Out of Scope

The classifier should not be used as the only security control.

It is not intended to:

- Replace human review for high-risk security decisions.
- Guarantee complete detection of prompt injection or malicious intent.
- Classify unrelated cybersecurity domains with high confidence.
- Make operational decisions in real SCADA environments.
- Measure system performance.

## 5. Inputs

The classifier receives a text prompt and request identifier.

Example:

```json
{
  "text": "Explain IEC 61850 at a high level.",
  "request_id": "uuid"
}
```

## 6. Outputs

The classifier returns a label and score.

Example:

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

## 7. Middleware Decision Logic

The middleware uses the classifier result as a security signal.

Decision behavior:

- `malicious`: reject the prompt and do not call Mistral.
- `suspicious`: evaluate local rules; high-risk matches can block the prompt.
- `safe`: continue through local rules and, if allowed, call Mistral.

The final decision can still be affected by local input rules and output rules.

## 8. Limitations

- False positives can block legitimate educational or defensive prompts.
- False negatives can allow unsafe prompts if local rules do not catch them.
- Quality depends on the classifier service operated by the RoBERTa owner.
- Classification alone does not inspect generated Mistral output.
- The middleware cannot improve classifier quality; it can only consume the returned label and score.

## 9. Safety Controls Around The Classifier

Use the classifier together with:

- Local input rules.
- Local output rules.
- Audit logging.
- Private network restrictions.
- Review of repeated malicious attempts by client host.

## 10. Security Metrics

Track security behavior, not runtime performance.

Relevant metrics:

- RoBERTa label distribution: `safe`, `suspicious`, `malicious`.
- Malicious prompt count.
- Malicious prompt rate.
- Suspicious prompt count.
- Blocked prompt count.
- Triggered rule frequency.
- False positive reports.
- False negative reports.
- RoBERTa unavailable events.

Not security metrics:

- Latency.
- Throughput.
- CPU usage.
- Token generation speed.

## 11. Degraded Behavior

If RoBERTa is unavailable, the middleware should return a degraded or unavailable response instead of silently allowing prompts to reach Mistral.

Common causes:

- `ROBERTA_URL` is unreachable.
- `ROBERTA_ENDPOINT` is incorrect.
- The external classifier service is down or misconfigured.
- Network timeout exceeded `REQUEST_TIMEOUT_SECONDS`.

# HackRx API

FastAPI implementation of `/hackrx/run` for the HackRx challenge.

## What it does
- Accepts a POST request with `documents` (PDF URL) and `questions` (array).
- Downloads PDF, extracts text, chunks it.
- Embeds chunks (OpenAI embeddings) and does similarity retrieval.
- Calls OpenAI ChatCompletion (GPT-4) with retrieved context to produce concise answers.
- Returns JSON: `{ "answers": [ ... ] }`.

## Endpoint
`POST /hackrx/run`
Headers:
- `Authorization: Bearer <API_KEY>`
- `Content-Type: application/json`

Body:
```json
{
  "documents": "https://example.com/policy.pdf",
  "questions": ["Question 1", "Question 2"]
}

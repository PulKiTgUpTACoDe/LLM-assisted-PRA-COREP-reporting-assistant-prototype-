# API Documentation

## Overview

The COREP Assistant API provides endpoints for processing regulatory queries and retrieving COREP template data.

**Base URL**: `http://localhost:8000`

## Authentication

Currently, no authentication is required (prototype).

## Endpoints

### Health Check

**GET** `/api/health`

Check API and service status.

**Response** (200 OK):

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "gemini_llm": "connected",
    "vector_db": "connected",
    "langchain": "ready"
  }
}
```

---

### List Templates

**GET** `/api/templates`

Get available COREP templates.

**Response** (200 OK):

```json
{
  "templates": [
    {
      "template_id": "CA1",
      "name": "Own Funds",
      "description": "COREP CA1 Own Funds template",
      "row_count": 40,
      "col_count": 3,
      "field_count": 120,
      "status": "available"
    }
  ]
}
```

---

### Process Query

**POST** `/api/query`

Process a natural language regulatory query.

**Request Body**:

```json
{
  "question": "Our bank has CET1 capital of £500M, AT1 of £100M, and Tier 2 of £50M. What should we report?",
  "template_id": "CA1",
  "context": {}
}
```

**Parameters**:

- `question` (string, required): Natural language scenario or question
- `template_id` (string, optional): Target template, default "CA1"
- `context` (object, optional): Additional context

**Response** (200 OK):

```json
{
  "query_id": "uuid-here",
  "template_id": "CA1",
  "template_name": "Own Funds (CA1)",
  "fields": [
    {
      "field_code": "C0010_R0010",
      "row_code": "R0010",
      "col_code": "C0010",
      "label": "Capital instruments and the related share premium accounts",
      "value": 500000000,
      "data_type": "numeric",
      "justification": "The scenario states CET1 capital of £500M...",
      "source_rules": ["CRR Article 26(1)", "CRR Article 28"],
      "confidence": "high"
    }
  ],
  "validation_issues": [
    {
      "field_code": "C0010_R0200",
      "severity": "warning",
      "message": "Required field R0200 is not populated",
      "suggestion": "Ensure this field is calculated or provided"
    }
  ],
  "audit_log": [
    {
      "field_code": "C0010_R0010",
      "value": 500000000,
      "reasoning": "Per CRR Article 26, CET1 includes capital instruments...",
      "source_rules": [
        {
          "rule_id": "CRR Article 26(1)",
          "rule_text": "Common Equity Tier 1 items shall comprise...",
          "relevance_score": "N/A"
        }
      ],
      "confidence": "high",
      "retrieved_at": "2026-02-07T12:00:00Z"
    }
  ],
  "missing_data": ["Breakdown of CET1 capital components not specified"],
  "assumptions": [
    "Assumed all CET1 capital is in ordinary shares and share premium"
  ],
  "metadata": {
    "processed_at": "2026-02-07T12:00:00.123Z",
    "documents_retrieved": 10,
    "fields_populated": 15,
    "orchestration_method": "langchain"
  }
}
```

**Error Responses**:

- **400 Bad Request**: Invalid question format
- **500 Internal Server Error**: Processing failed

---

## Data Models

### TemplateField

| Field           | Type          | Description                            |
| --------------- | ------------- | -------------------------------------- |
| `field_code`    | string        | COREP field code (e.g., "C0010_R0010") |
| `row_code`      | string        | Row identifier                         |
| `col_code`      | string        | Column identifier                      |
| `label`         | string        | Human-readable field label             |
| `value`         | number/string | Populated value                        |
| `data_type`     | string        | Data type ("numeric", "text", "date")  |
| `justification` | string        | Explanation for the value              |
| `source_rules`  | string[]      | List of regulatory rules used          |
| `confidence`    | string        | "high", "medium", "low", "unknown"     |

### ValidationIssue

| Field        | Type   | Description                |
| ------------ | ------ | -------------------------- |
| `field_code` | string | Affected field             |
| `severity`   | string | "error", "warning", "info" |
| `message`    | string | Issue description          |
| `suggestion` | string | Recommended fix            |

### AuditLogEntry

| Field          | Type     | Description              |
| -------------- | -------- | ------------------------ |
| `field_code`   | string   | Field identifier         |
| `value`        | any      | Field value              |
| `reasoning`    | string   | LLM reasoning            |
| `source_rules` | object[] | Rules with text snippets |
| `confidence`   | string   | Confidence level         |
| `retrieved_at` | string   | ISO timestamp            |

---

## Rate Limits

No rate limits currently (prototype).

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bank has CET1: £500M, AT1: £100M, Tier 2: £50M",
    "template_id": "CA1"
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "question": "Our bank has CET1 capital of £500M...",
        "template_id": "CA1"
    }
)

data = response.json()
print(f"Populated {len(data['fields'])} fields")
```

### JavaScript

```javascript
const response = await fetch("http://localhost:8000/api/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: "Our bank has CET1 capital of £500M...",
    template_id: "CA1",
  }),
});

const data = await response.json();
console.log(`Populated ${data.fields.length} fields`);
```

---

For interactive API documentation, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

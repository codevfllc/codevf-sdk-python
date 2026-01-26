# CodeVF Python SDK

The official Python library for the [CodeVF API](https://codevf.com). This SDK provides a simple and typed interface to interact with CodeVF's engineering automation platform.

## Installation

```bash
pip install codevf-sdk
```

## Authentication

The SDK requires an API key. You can provide it directly during initialization, export it via `CODEVF_API_KEY`,
or let your deployment inject a long-lived bearer token that carries the necessary scopes.

### Authorization header

All API requests must include the following header:

```
Authorization: Bearer sk_live_... (or sk_test_...)
```

The header value is the API key issued by CodeVF; the header name is case-insensitive and additional headers such as
`Content-Type: application/json` are required when submitting JSON bodies.

### Token type, scopes, and expiration

| Field       | Description                                                                                                                                                                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Token type  | Bearer token (`sk_...`) with at least one of the scopes listed below. Tokens resemble JWTs but are opaque to the SDK.                                                                                                                                                     |
| Scopes      | `projects:write`, `tasks:write`, `tasks:read`, `credits:read`. Each token is granted a subset of these scopes and requests lacking the required scope will return 403 with `error: "insufficient_scope"`.                                                                 |
| Expiration  | Tokens expire 90 days after issuance. When a request fails with 401 and `error: "token_expired"`, rotate the token in the Console or via the Management API. SDK users are encouraged to refresh their `CODEVF_API_KEY` before expiration to avoid interruptions.         |
| Scope model | `projects:write` covers project creation. `tasks:write` lets you submit tasks and attachments. `tasks:read` allows polling `GET /tasks/{id}`. `credits:read` covers `GET /credits/balance`. Tokens without the required scope are not usable for the associated endpoint. |

You can still instantiate the client with `CODEVF_API_KEY` in the shell:

```bash
# export CODEVF_API_KEY="sk_live_..."
client = CodeVFClient()
```

### Example request with authentication

```bash
curl -X POST "https://api.codevf.com/projects/create" \
  -H "Authorization: Bearer sk_live_123abc" \
  -H "Content-Type: application/json" \
  -d '{"name": "My API Project", "description": "Group of automation tasks"}'
```

The SDK automatically injects the same header when you pass `api_key` or rely on `CODEVF_API_KEY`.

## Quick Start

### 1. Manage Projects

Group your tasks by creating projects.

```python
project = client.projects.create(
    name="Data Analysis Pipeline",
    description="Automating pandas-based processing scripts"
)
print(f"Created Project ID: {project.id}")
```

Project creation is scoped to your account, and project `name` must be unique per user. When you call `POST /projects/create`, the API first looks for an existing project with the same name. If it exists, the endpoint returns the existing project resource (HTTP 200) so you can safely `create` without duplicating work. If it does not exist, a new project is created and HTTP 201 is returned with the newly minted `id`. This “create or reuse” behavior means SDK callers do not need to list projects before creating one; simply pass the desired name and optional description each time.

If you need to update a project’s metadata later, use the dedicated management console or a future endpoint; the `description` parameter is only applied when the project is first created. Calling `create` with a name that already exists never results in a conflict error—only the existing project payload is returned—so your client can cache the returned `id` for subsequent tasks.

### 2. Create and Monitor Tasks

Submit engineering prompts and monitor their execution.

```python
from codevf import ServiceMode, calculate_final_credit_cost, validate_metadata
from decimal import Decimal

metadata = validate_metadata({"environment": "production"})
project_tag = 3

# Submit a task
task = client.tasks.create(
    prompt="Refactor this script to use vectorized operations.",
    max_credits=30,
    project_id=project.id,
    mode=ServiceMode.FAST,
    metadata=metadata,
    tag_id=project_tag,
    attachments=[
        {
            "fileName": "process.py",
            "mimeType": "text/x-python",
            "content": "for i in range(len(df)): df.iloc[i] = df.iloc[i] * 2"
        }
    ]
)

# Check status
status = client.tasks.retrieve(task.id)
print(f"Task Status: {status.status}")

# Estimate cost before you submit
estimated = calculate_final_credit_cost(30, ServiceMode.FAST, Decimal("1.7"))
print(f"Estimated credits held: {estimated}")
```

### 3. Check Credit Balance

Monitor your usage and available resources.

```python
balance = client.credits.get_balance()
print(f"Available: {balance['available']} credits")
```

## SDK architecture

The SDK splits responsibilities into four layers:

1. **Client core** (`CodeVFClient`) manages HTTP retries, authentication, and request/response plumbing.
2. **Resources** (`Projects`, `Tasks`, `Credits`, `Tags`) wrap specific API paths and return typed models.
3. **Models** (`Project`, `TaskResponse`, `CreditBalance`, `Tag`) describe structured payloads and helpers like `calculate_final_credit_cost` for projecting spend.
4. **Utilities** (`validate_metadata`, attachment normalization helpers) enforce metadata shapes and attachment limits before they are sent.

```python
from decimal import Decimal
from codevf import (
    CodeVFClient,
    ServiceMode,
    calculate_final_credit_cost,
    validate_metadata,
)

client = CodeVFClient(api_key="sk_test_...")
metadata = validate_metadata({"environment": "production"})
estimated = calculate_final_credit_cost(30, ServiceMode.FAST, Decimal("1.7"))
```

## Running the smoke script

After installing the SDK (or `pip install -e .` in dev), you can exercise the core endpoints with `scripts/integration_smoke.py`. Export your live/test API key before running:

```bash
export CODEVF_API_KEY="sk_live_..."
python scripts/integration_smoke.py
```

The script creates or reuses a project, lists tags, submits + polls a task, cancels a second task, and prints your latest credit balance, demonstrating each endpoint.

## Task lifecycle, polling, and validation

### Polling guidelines for `GET /tasks/{id}`

The SDK should poll `GET /tasks/{id}` to track the status of each task. Adhere to the documented rate limits (1 request per second, 3,600 per hour) and honor any `Retry-After` header returned with `429 Too Many Requests` or `503 Service Unavailable`. Recommended polling cadence:

1. Wait ~2 seconds after `POST /tasks/create` before the first poll.
2. If `status` remains `pending`, continue polling every 2–4 seconds.
3. Once `status` is `processing`, slow polling to every 5–10 seconds for `fast` mode tasks and every 15–30 seconds for `standard` tasks.
4. Cease polling immediately when `status` becomes `completed` or `cancelled`.

Statuses:

| Status       | Meaning                                               | Notes for SDKs                                                            |
| ------------ | ----------------------------------------------------- | ------------------------------------------------------------------------- |
| `pending`    | The request is queued; work has not started.          | Continue polling but do not exceed rate limits.                           |
| `processing` | A human engineer is working on the task.              | Clients may read partial results; continue polling with longer intervals. |
| `completed`  | Task finished; `result` and `deliverables` are final. | Stop polling and deliver payload to callers.                              |
| `cancelled`  | Task was stopped (user cancel or timeout).            | Surface to callers; no further polling required.                          |

`GET /tasks/{id}` may include a `Retry-After` header even on `200 OK` when the backend needs more time; treat that as a hint to wait before the next poll. When the server returns `429`, back off according to the header and resume polling once the window expires.

### Mode, tag, and metadata validation

`POST /tasks/create` validates the following fields and returns HTTP 400 with `error: "invalid_<field>"` if anything fails:

| Parameter  | Allowed values                                                                         | Default                                     | Validation notes                                                                                                                   |
| ---------- | -------------------------------------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `mode`     | `"realtime_answer"`, `"fast"`, `"standard"`                                            | `"standard"`                                | Invalid options cause `invalid_mode`. Each string maps to SLA multipliers of 2×, 1.5×, and 1× respectively.                        |
| `tagId`    | Integer from `GET /tags` where `isActive` is `true`                                    | `general_purpose` tag (costMultiplier 1.00) | SDKs should call `GET /tags` to cache available IDs. Inactive or unknown IDs trigger `invalid_tag`.                                |
| `metadata` | Flat JSON object with string keys and primitive values (`string`, `number`, `boolean`) | `{}`                                        | Nested arrays/objects are rejected with `invalid_metadata`. Keys should be alphanumeric/underscore to allow future search filters. |

SDKs should validate these values before sending requests to fail fast and provide clear error messages to callers.

### Max credits enforcement

`maxCredits` must be an integer between 1 and 1,920 inclusive. The API calculates the total cost immediately using:

```
finalCost = maxCredits × slaMultiplier × tagMultiplier
```

Multipliers are applied when the task is accepted. The returned `creditsUsed` (in `GET /tasks/{id}`) is always rounded **up** to the next whole number to guarantee the platform has enough credits even when multipliers produce fractions. If `finalCost` exceeds the provided `maxCredits`, the request is rejected with HTTP 402 and `error: "max_credits_exceeded"`. SDKs should surface this error so callers can raise `maxCredits` or choose a less expensive mode/tag before retrying.

Example:

```python
max_credits = 30
mode = "fast"  # 1.5× SLA multiplier
tag_multiplier = 1.7  # Engineer tag
calculated = max_credits * 1.5 * 1.7  # = 76.5
# Server stores 77 credits and rejects if maxCredits < 77
```

When submitting tasks, SDK helpers should expose projected cost and rounding so callers can choose appropriate limits without trial-and-error.

### Idempotency semantics

`POST /tasks/create` accepts an optional `idempotencyKey` (UUID v4) that is scoped to the authenticated API key and the endpoint path. For each API key, the service remembers the key for 24 hours; any repeat request with the same `idempotencyKey` returns the original task payload (HTTP 200) regardless of how many times it is submitted. If a different API key attempts to reuse another key’s value, the server rejects it with HTTP 409 and `error: "idempotency_conflict"`. The response when a key is reused includes the original `id` and `status`, so SDKs can safely `GET /tasks/{id}` without re-submitting work.

If the original request failed with a non-success (e.g., HTTP 500), the client may retry with the same key once the initial request has returned, but it should drop the key after a successful submission to avoid storage growth. When the server evicts the key after 24 hours, a new request can use the same value again.

### Attachments and payload encoding

Attachments are sent as part of the JSON payload under the `attachments` array (`POST /tasks/create`). Each attachment needs the following fields: `fileName`, `mimeType`, and either `content` (raw text for textual formats) or `content` containing base64-encoded bytes for binaries. The API does not accept multipart/form-data — everything stays inside JSON. The SDK must validate each attachment before sending:

1. Text-based files and logs (e.g., `.py`, `.json`, `.txt`) must be sent as UTF-8 strings inside `content`.
2. Binary blobs (images, PDFs) must be base64-encoded and stored in `content`. The SDK should not add a separate `base64` key.
3. File size limits: textual attachments may not exceed 1 MB (1,048,576 bytes) before encoding; binary attachments may not exceed 10 MB after base64 encoding. Clients should compute the size locally and raise `AttachmentTooLargeError` before issuing the request to avoid `413 Payload Too Large`.
4. The service enforces a maximum of five attachments per task; exceeding this limit returns HTTP 400 with `error: "attachment_limit_exceeded"`.

### Error response schema

All error responses follow a consistent JSON shape:

```json
{
  "error": {
    "code": "invalid_mode",
    "message": "mode must be one of realtime_answer, fast, or standard",
    "status": 400,
    "retryable": false
  }
}
```

| Field       | Description                                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| `code`      | Machine-readable error identifier. SDKs should map this to typed exceptions (e.g., `InvalidModeError`).         |
| `message`   | Human-readable explanation of what went wrong.                                                                  |
| `status`    | HTTP status code for reference.                                                                                 |
| `retryable` | Boolean indicating whether the client may safely retry the request (`true` for 429/500/503, `false` otherwise). |

Retryable errors (`retryable: true`) include 429, 500, and 503 and must supply a `Retry-After` header. Non-retryable errors (401, 402, 404, 413, 409, etc.) set `retryable: false`. SDKs should raise distinct exception types so callers can react (e.g., prompt for more credits, refresh credentials, increase `maxCredits`, or stop retry loops). If the response deviates from the schema (legacy clients), fall back to the legacy `{ "error": "...", "status": ... }` format.

## Error Handling

The SDK maps API error codes to specific Python exceptions for robust error handling.

```python
from codevf.exceptions import AuthenticationError, RateLimitError, APIError

try:
    client.projects.create(name="New Project")
except AuthenticationError:
    print("Invalid API Key")
except RateLimitError:
    print("API limit reached")
except APIError as e:
    print(f"Request failed: {e.message}")
```

## Supplementary SDK endpoints

To keep the Python SDK ergonomic and strongly typed, the following companion endpoints (not yet part of the original spec) should still be published. They all follow the same base URL (`/projects`, `/tasks`, `/tags`) and return JSON objects with consistent paging envelopes.

| Endpoint                       | Use case                                              | Request/response highlights                                                                                                                                                                                                                                                      |
| ------------------------------ | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /projects`                | List all projects for the authenticated user          | Supports `page`, `pageSize`, and optional `name` filter. Response: `{ "data": [ { "id": 123, "name": "...", "description": "...", "createdAt": "..."} ], "page": 1, "pageSize": 20, "total": 42 }`. Clients can cache IDs or reconcile when `POST /projects/create` returns 200. |
| `GET /projects/{id}`           | Fetch metadata for a specific project                 | Response mirrors the create payload plus timestamps; returns 404 if unauthorized.                                                                                                                                                                                                |
| `GET /tasks`                   | List a user’s tasks with filtering                    | Allows `projectId`, `status`, `mode`, `tagId`, `since`, `page`, `pageSize`. Response: paginated envelope with tasks summaries (id, status, createdAt, creditsUsed).                                                                                                              |
| `GET /tasks/{id}/deliverables` | Retrieve deliverables without re-fetching entire task | Returns `deliverables` array with `fileName`, `url`, `mimeType`, `uploadedAt`. This keeps repeated polling lean when you just need attachments.                                                                                                                                  |
| `GET /tags`                    | List active/inactive tags and their multipliers       | Response already exists; extend it to include `validFrom`, `validTo`, and `isDeprecated` so SDKs know when to refresh cached values.                                                                                                                                             |

Use `client.tags.list()` to surface these tag records as typed `Tag` models, including `costMultiplier`, `isActive`, and deprecation hints.

Each endpoint should reject invalid pagination values with HTTP 400 and obey the same `Authorization` header/scopes (e.g., `projects:read`, `tasks:read`, `tags:read`). Implement stable typing by modeling responses as typed dataclasses or `TypedDict`s in the SDK; include `total`, `page`, and `pageSize` to support pagination helpers.

## Features

- **Resource Management**: Easy access to Projects, Tasks, Credits, and Tags with dedicated methods.
- **Type Safety**: Strongly typed models, helper functions (`calculate_final_credit_cost`, `validate_metadata`), and structured deliverables.
- **Resilience**: Built-in retry logic for transient network issues.
- **File Support**: First-class support for code and image attachments, with attachment validation utilities.

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/codevf/codevf-sdk-python.git
pip install -e .[dev]

# Run the test suite
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

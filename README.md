# CodeVF Python SDK

The official Python client for the [CodeVF API](https://codevf.com). This SDK provides a synchronous, typed wrapper around CodeVF's engineering automation platform to help you manage projects, submit human-review prompts, monitor credits, and choose engineer expertise levels.

## Features

- **Project Management** – Create and organize reusable projects that group related tasks.
- **Task Submission** – Submit prompts, attachments, metadata, and SLA mode preferences for human engineer review.
- **Credit System** – Monitor available, on-hold, and total credits so you can budget work before submission.
- **Engineer Expertise** – Fetch tag metadata and choose expertise levels with documented cost multipliers.
- **File Attachments** – Attach code files, logs, screenshots, and other assets with helper validation to stay within size limits.
- **Comprehensive Error Handling** – Typed exceptions for each HTTP failure mode, plus helpers for retries and validation.

## Quick Start

### Installation

```bash
pip install codevf-sdk
```

### Basic Usage

```python
from decimal import Decimal

from codevf import (
    CodeVFClient,
    ServiceMode,
    calculate_final_credit_cost,
    validate_metadata,
)

client = CodeVFClient(api_key="cvf_live_...")

project = client.projects.create(
    name="API Automation",
    description="Unify reliability checks for the new integration",
)

metadata = validate_metadata({"environment": "production"})
estimate = calculate_final_credit_cost(50, ServiceMode.FAST, Decimal("1.6"))

task = client.tasks.create(
    prompt="Review and document this authentication flow.",
    max_credits=50,
    project_id=project.id,
    mode=ServiceMode.FAST,
    metadata=metadata,
    attachments=[
        {"fileName": "auth.md", "mimeType": "text/markdown", "content": "# audit notes"},
    ],
)

status = client.tasks.retrieve(task.id)
balance = client.credits.get_balance()
tags = client.tags.list()
```

Initialize the client with `CodeVFClient`, create a project, submit a task with metadata and attachments, then poll its status and check your credit balance. Use `tags.list()` to discover engineer expertise levels and associated cost multipliers before choosing a `tag_id`.

## Architecture

The SDK mirrors the API surface with a clear separation of concerns:

- **Core** — `CodeVFClient` (`src/codevf/client.py`) handles authentication, retries, base URL configuration, and request plumbing.
- **Resources** — `Projects`, `Tasks`, `Credits`, and `Tags` in `src/codevf/resources` wrap each API domain and normalize payloads into typed models.
- **Models** — `src/codevf/models` defines `Project`, `TaskResponse`, `CreditBalance`, `Tag`, `TaskDeliverable`, and helpers such as `calculate_final_credit_cost` and `normalize_attachments`.
- **Utilities** — helpers such as `validate_metadata` enforce metadata rules and attachment limits before requests go out.

## API Reference

### Projects

- `client.projects.create(name, description=None)` — create or reuse a named project and receive a `Project` model.

### Tasks

- `client.tasks.create(...)` — submit prompts, attachments, metadata, tag IDs, SLA modes, and optional idempotency keys; the helper enforces prompt length, credit bounds, and attachment limits before making the request.
- `client.tasks.retrieve(task_id)` — poll task status, deliverables, and credit usage.
- `client.tasks.cancel(task_id)` — cancel pending or processing tasks.

### Credits

- `client.credits.get_balance()` — retrieve a `CreditBalance` object with `available`, `on_hold`, and `total` credits.

### Tags

- `client.tags.list()` — list engineer expertise tags with `cost_multiplier`, `is_active`, and metadata to help you pick the right expertise level.

## Error Handling

Typed exceptions in `codevf.exceptions` map raw API responses to actionable error classes so you can respond precisely to each failure mode. Common exceptions include `AuthenticationError` (401/403), `RateLimitError` (429), `MaxCreditsExceededError`, `InvalidModeError`, `InvalidTagError`, `InvalidMetadataError`, `InsufficientCreditsError`, `AttachmentLimitExceededError`, `AttachmentTooLargeError`, `PayloadTooLargeError`, `ServerError` (5xx), and `APIConnectionError`.

```python
from codevf.exceptions import AuthenticationError, RateLimitError

try:
    client.credits.get_balance()
except AuthenticationError:
    # refresh the API key or rotate your environment secret
    ...
except RateLimitError:
    # honor Retry-After before retrying
    ...
```

## Running Tests

```bash
pytest
```

Tests live under `/tests` and mirror the package structure to keep fixtures aligned with production resources.

## Smoke Script

The `scripts/integration_smoke.py` script walks through the core endpoints (project creation/reuse, tag listing, task submission/cancellation, and balance checks). Export your API key before running:

```bash
export CODEVF_API_KEY="cvf_live_..."  # use `setx` or PowerShell's `Set-Item` on Windows
python scripts/integration_smoke.py
```

## Development

```bash
git clone https://github.com/codevf/codevf-sdk-python.git
pip install -e .[dev]

pytest
ruff check src tests
mypy
```

Install dev dependencies with `pip install -e .[dev]`, then run `pytest`, `ruff check`, and `mypy` for linting and type coverage.

## Requirements

- Python 3.9 or newer
- `requests>=2.25.0`
- Optional dev dependencies: `pytest`, `ruff`, `mypy`, `types-requests`

## License

MIT — see the [LICENSE](LICENSE) file for details.

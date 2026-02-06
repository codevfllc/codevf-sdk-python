# CodeVF Python SDK

The official Python client for the [CodeVF API](https://codevf.com). This SDK helps you manage projects, submit tasks for human review, and monitor your credits.

## Installation

```bash
pip install codevf-sdk
```

## Quick Start

### 1. Authentication

The client looks for the `CODEVF_API_KEY` environment variable by default.

```bash
export CODEVF_API_KEY="cvf_live_..."
```

Or you can pass it directly:

```python
from codevf import CodeVFClient

client = CodeVFClient(api_key="cvf_live_...")
```

### 2. Verify Connection

Check your account balance to verify connectivity:

```python
from codevf import CodeVFClient

client = CodeVFClient()
balance = client.credits.get_balance()

print(f"Available Credits: {balance.available}")
```

### 3. Submitting a Task

Here is a complete example of creating a project and submitting a task.

```python
from codevf import CodeVFClient, ServiceMode

client = CodeVFClient()

# 1. Create a project to organize your tasks
project = client.projects.create(
    name="API Migration",
    description="Tasks related to the v2 migration"  # Optional
)

# 2. Submit a task for review
task = client.tasks.create(
    prompt="Check this code for security vulnerabilities.",
    max_credits=240,
    project_id=project.id,
    mode=ServiceMode.FAST,          # Optional: defaults to STANDARD
    # metadata={"env": "prod"},     # Optional: custom tags
    # attachments=[...],            # Optional: file attachments
)

print(f"Task submitted! ID: {task.id}")

# 3. Check status
current_task = client.tasks.retrieve(task.id)
print(f"Status: {current_task.status}")
```

## Features

- **Project Management** - Create and organize reusable projects.
- **Task Submission** - Submit prompts with code files and instructions for human engineers.
- **Credit System** - Monitor your available budget.
- **Engineer Expertise** - Choose expertise levels (Tags) to match the task difficulty.
- **Attachments** - Upload files, logs, or screenshots.
- **Error Handling** - Typed exceptions for easy debugging and retries.

## Architecture

The SDK mirrors the API surface:

- **Core** - `CodeVFClient` handles authentication and requests.
- **Resources** - `client.projects`, `client.tasks`, `client.credits`, etc.
- **Models** - Typed objects like `Project`, `TaskResponse`, `CreditBalance`.

## API Reference

### Projects

```python
# Create a new project
project = client.projects.create(name="My Project")
```

### Tasks

```python
# Submit a task
client.tasks.create(
    prompt="Refactor this function",
    max_credits=240,
    project_id=123
)

# Check status
client.tasks.retrieve(task_id="...")

# Cancel
client.tasks.cancel(task_id="...")
```

### Credits

```python
# Check balance
client.credits.get_balance()
```

### Tags

```python
# List available expertise levels
client.tags.list()
```

## Task Credits and Modes

- `realtime_answer`: 60-600 credits, 2x multiplier
- `fast`: 240-115200 credits, 1.5x multiplier
- `standard`: 240-115200 credits, 1x multiplier

The SDK validates these ranges client-side.

## Attachments

- Max 5 attachments per task
- Images (PNG/JPG/GIF/WebP): up to 10MB, base64-encoded
- PDFs: up to 10MB, base64-encoded
- Source code and text files (PY/JS/JSON/MD/etc.): up to 1MB, raw text

## Error Handling

Exceptions are available in `codevf.exceptions`:

```python
from codevf.exceptions import AuthenticationError, RateLimitError

try:
    client.credits.get_balance()
except AuthenticationError:
    print("Check your API key")
except RateLimitError:
    print("Slow down!")
```

## Development

```bash
git clone https://github.com/codevf/codevf-sdk-python.git
cd codevf-sdk-python

# Install dependencies
pip install -e .[dev]

# Run tests
pytest
```

## License

MIT - see the [LICENSE](LICENSE) file for details.

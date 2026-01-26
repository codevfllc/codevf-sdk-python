# CodeVF Python SDK

The official Python library for the [CodeVF API](https://codevf.com). This SDK provides a simple and typed interface to interact with CodeVF's engineering automation platform.

## Installation

```bash
pip install codevf-sdk
```

## Authentication

The SDK requires an API key. You can provide it directly during initialization or set the `CODEVF_API_KEY` environment variable.

```python
from codevf import CodeVFClient

# Explicit initialization
client = CodeVFClient(api_key="your_api_key_here")

# Environment-based initialization (recommended)
# export CODEVF_API_KEY="your_api_key_here"
client = CodeVFClient()
```

## Quick Start

### 1. Manage Projects
Group your tasks by creating projects.

```python
project = client.projects.create(
    name="Data Analysis Pipeline",
    description="Automating pandas-based processing scripts"
)
print(f"Created Project ID: {project['id']}")
```

### 2. Create and Monitor Tasks
Submit engineering prompts and monitor their execution.

```python
# Submit a task
task = client.tasks.create(
    prompt="Refactor this script to use vectorized operations.",
    max_credits=20,
    project_id=project['id'],
    attachments=[
        {
            "fileName": "process.py",
            "mimeType": "text/x-python",
            "content": "for i in range(len(df)): df.iloc[i] = df.iloc[i] * 2"
        }
    ]
)

# Check status
status = client.tasks.retrieve(task['id'])
print(f"Task Status: {status['status']}")
```

### 3. Check Credit Balance
Monitor your usage and available resources.

```python
balance = client.credits.get_balance()
print(f"Available: {balance['available']} credits")
```

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

## Features

- **Resource Management**: Easy access to Projects, Tasks, and Credits.
- **Type Safety**: Fully typed methods and responses.
- **Resilience**: Built-in retry logic for transient network issues.
- **File Support**: First-class support for code and image attachments.

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
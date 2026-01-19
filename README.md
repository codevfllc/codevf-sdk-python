# CodeVF Python SDK

The official Python library for the CodeVF API.

## Installation

```bash
pip install codevf-sdk
```

## Usage

The SDK requires an API key. You can pass it directly to the client or set the `CODEVF_API_KEY` environment variable.

```python
import os
from codevf import CodeVFClient, APIError

# Initialize the client
client = CodeVFClient(api_key="your_api_key")

# Or if environment variable CODEVF_API_KEY is set:
# client = CodeVFClient()

try:
    # Make a request (example)
    # Note: Replace 'projects' with actual endpoints when available
    response = client.get("projects")
    print(response)
    
except APIError as e:
### Credits

Check your current credit balance:

```python
balance = client.credits.get_balance()
print(f"Available credits: {balance['available']}")
print(f"Total credits: {balance['total']}")
```

## Features

- **Automatic Authentication**: Handles Bearer token headers.
- **Error Handling**: Maps HTTP status codes to typed exceptions (e.g., `NotFoundError`, `RateLimitError`).
- **Session Management**: Uses `requests.Session` for connection pooling.
- **Type Hinting**: Fully typed for better development experience.

## Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Run tests:
   ```bash
   pytest
   ```

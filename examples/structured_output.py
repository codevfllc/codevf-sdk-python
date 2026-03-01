import os
import json
import time
from codevf import CodeVFClient

# Configuration helper for environment variables
def load_env_file(path: str = ".env") -> None:
    """Manually parse a .env file to avoid extra dependencies like python-dotenv."""
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                # Only set if not already in environment
                if key.strip() not in os.environ:
                    os.environ[key.strip()] = value.strip().strip("'\"")

def get_config(key: str, default: str = "") -> str:
    """Helper to fetch environment variables with clean values."""
    value = os.environ.get(key, default)
    return value.strip("'\"")

def main():
    # Load .env if it exists in current or parent directory
    load_env_file()
    if not os.environ.get("CODEVF_API_KEY"):
        load_env_file("codevf-sdk-python/.env")

    # 1. Initialize the client
    api_key = get_config("CODEVF_API_KEY")
    if not api_key:
        print("Error: CODEVF_API_KEY environment variable is not set.")
        print("Please set it: export CODEVF_API_KEY='your-key-here' (Linux/macOS) or $env:CODEVF_API_KEY='your-key-here' (PowerShell)")
        return

    base_url = get_config("CODEVF_BASE_URL", "https://codevf.com/api/v1/")
    client = CodeVFClient(api_key=api_key, base_url=base_url)

    # 2. Define a JSON Schema for the structured output you want
    schema = {
        "type": "object",
        "properties": {
            "vulnerabilities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": { 
                            "type": "string", 
                            "enum": ["critical", "high", "medium", "low"] 
                        },
                        "description": { "type": "string" },
                        "location": { "type": "string" },
                        "recommendation": { "type": "string" }
                    },
                    "required": ["severity", "description"]
                }
            },
            "securityScore": { 
                "type": "number", 
                "minimum": 0, 
                "maximum": 100 
            }
        },
        "required": ["vulnerabilities", "securityScore"]
    }

    print("Submitting task with response_schema and attachments...")
    
    # 3. Create a task with response_schema
    # Using realtime_answer mode for instant results
    prompt = (
        "Analyze this code for security issues, considering the database configuration in the attachment:\n\n"
        "def login(user, pwd):\n"
        "    query = f\"SELECT * FROM users WHERE user='{user}' AND pwd='{pwd}'\"\n"
        "    return db.execute(query)"
    )
    
    # Attachments can provide additional context for the analysis
    attachments = [
        {
            "fileName": "db_config.py",
            "mimeType": "text/x-python",
            "content": "DB_HOST = 'localhost'\nDB_USER = 'admin'\nDB_PASS = '123456'\nDB_NAME = 'production_db'"
        }
    ]
    
    project_id = int(get_config("CODEVF_PROJECT_ID", "1"))
    
    try:
        task = client.tasks.create(
            prompt=prompt,
            project_id=project_id,
            max_credits=60,
            mode="realtime_answer",
            response_schema=schema,
            attachments=attachments
        )
    except Exception as e:
        print(f"Failed to create task: {e}")
        return

    print(f"Task created: {task.id}, Status: {task.status}")

    # 4. Handle results
    # For realtime_answer, the result might be available immediately
    if task.status == "completed":
        print("\nStructured Result received immediately:")
        if isinstance(task.result, dict):
            # When response_schema is used, result is returned as a raw dict
            print(json.dumps(task.result, indent=2))
        else:
            # Fallback for standard result
            print(f"Message: {task.result.message}")
    else:
        # For other modes or if not immediately finished, poll until completed
        print("\nWaiting for task completion...")
        while task.status not in ["completed", "cancelled"]:
            time.sleep(2)
            task = client.tasks.retrieve(task.id)
            print(f"Status: {task.status}")

        if task.status == "completed":
            print("\nResult received:")
            if isinstance(task.result, dict):
                print(json.dumps(task.result, indent=2))
            else:
                print(f"Message: {task.result.message}")
        else:
            print(f"\nTask ended with status: {task.status}")

if __name__ == "__main__":
    main()

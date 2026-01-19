import os
import sys
from codevf import CodeVFClient
from codevf.exceptions import CodeVFError

# Ensure the package is in the path for this example if run directly from source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def main():
    # Initialize the client
    # Assumes CODEVF_API_KEY is set in environment variables
    # or you can pass it directly: client = CodeVFClient(api_key="your_api_key")
    try:
        client = CodeVFClient()
    except Exception as e:
        print(f"Error initializing client: {e}")
        print("Please set CODEVF_API_KEY environment variable.")
        return

    try:
        print("Creating a new task...")

        # Define attachments
        attachments = [
            {
                "fileName": "requirements.txt",
                "mimeType": "text/plain",
                "content": "pandas>=1.3.0\nnumpy>=1.21.0"
            },
            {
                "fileName": "screenshot.png",
                "mimeType": "image/png",
                "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            }
        ]

        # Create the task
        task = client.tasks.create(
            prompt="Please analyze the attached requirements and implement a basic data processing script.",
            max_credits=50,
            project_id=123,
            mode="standard",
            metadata={"priority": "high", "department": "analytics"},
            attachments=attachments,
            tag_id=5
        )

        print("\nTask created successfully!")
        print(f"Task ID: {task.get('id')}")
        print(f"Status: {task.get('status')}")
        print(f"Mode: {task.get('mode')}")
        print(f"Credits: {task.get('maxCredits')}")
        print(f"Created At: {task.get('createdAt')}")

    except CodeVFError as e:
        print(f"\nAPI Error: {e}")
        if hasattr(e, 'body'):
            print(f"Error details: {e.body}")
    except ValueError as e:
        print(f"\nValidation Error: {e}")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")

if __name__ == "__main__":
    main()

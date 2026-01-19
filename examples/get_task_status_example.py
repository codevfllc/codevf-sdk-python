import os
import sys
import time
from codevf import CodeVFClient
from codevf.exceptions import CodeVFError

# Ensure the package is in the path for this example if run directly from source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def main():
    # Initialize the client
    # Assumes CODEVF_API_KEY is set in environment variables
    try:
        client = CodeVFClient()
    except Exception as e:
        print(f"Error initializing client: {e}")
        return

    # Replace with a real task ID you've created
    task_id = "task_your_id_here" 

    try:
        print(f"Checking status for task: {task_id}")
        
        # Retrieve the task
        task = client.tasks.retrieve(task_id)
        
        status = task.get("status")
        print(f"Current Status: {status}")

        if status == "completed":
            print("\nTask Completed!")
            print(f"Credits Used: {task.get('creditsUsed')}")
            
            result = task.get("result", {{}})
            print(f"Message: {result.get('message')}")
            
            deliverables = result.get("deliverables", [])
            if deliverables:
                print("\nDeliverables:")
                for item in deliverables:
                    print(f"- File: {item.get('fileName')}")
                    print(f"  URL: {item.get('url')}")
                    print(f"  Uploaded At: {item.get('uploadedAt')}")
            else:
                print("\nNo deliverables found.")

        elif status == "pending" or status == "processing":
            print("\nTask is still in progress. Please check again later.")
            
        elif status == "cancelled":
            print("\nTask was cancelled.")
            
        else:
            print(f"\nUnknown task status: {status}")

    except CodeVFError as e:
        print(f"\nAPI Error: {e}")
    except ValueError as e:
        print(f"\nValidation Error: {e}")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")

if __name__ == "__main__":
    main()

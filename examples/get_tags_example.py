import os
import sys
from codevf import CodeVFClient
from codevf.exceptions import CodeVFError

# Ensure the package is in the path for this example if run directly from source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

def main():
    """
    This example demonstrates how to retrieve available expertise tags
    and use a tagId when creating a task.
    """
    # Initialize the client
    # Assumes CODEVF_API_KEY is set in environment variables
    try:
        client = CodeVFClient()
    except Exception as e:
        print(f"Error initializing client: {e}")
        return

    try:
        print("--- Retrieving Available Expertise Tags ---")
        
        # 1. Fetch available tags
        # Each tag represents an engineer expertise level with a cost multiplier.
        tags = client.tags.list()
        
        selected_tag_id = None
        
        if not tags:
            print("No tags available.")
        else:
            print(f"{'ID':<5} {'Display Name':<25} {'Multiplier':<12} {'Active'}")
            print("-" * 55)
            
            for tag in tags:
                tag_id = tag.get("id")
                display_name = tag.get("displayName")
                multiplier = tag.get("costMultiplier")
                is_active = tag.get("isActive")
                
                print(f"{tag_id:<5} {display_name:<25} {multiplier:<12.2f} {is_active}")
                
                # For this example, let's pick the 'Expert' tag if it exists
                if tag.get("name") == "expert" and is_active:
                    selected_tag_id = tag_id

        # 2. Use a tag_id in task creation
        if selected_tag_id:
            print(f"\n--- Creating Task with Tag ID: {selected_tag_id} ---")
            
            # The final credits will be: base credits * SLA multiplier * tag multiplier
            # Example: 10 base credits * 1.0 SLA * 1.5 expert multiplier = 15 credits
            
            task = client.tasks.create(
                prompt="Implement a high-performance sorting algorithm in Python.",
                max_credits=100,
                project_id=1,  # Replace with a valid project ID
                tag_id=selected_tag_id
            )
            
            print(f"Task created successfully! ID: {task.get('id')}")
            print(f"Status: {task.get('status')}")
        else:
            print("\nSkipping task creation because no suitable tag was found.")

    except CodeVFError as e:
        print(f"\nAPI Error: {e}")
        if hasattr(e, 'body'):
            print(f"Error details: {e.body}")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")

if __name__ == "__main__":
    main()

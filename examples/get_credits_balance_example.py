import os
from codevf import CodeVFClient

def main():
    # Initialize the client with your API key
    # You can also set the CODEVF_API_KEY environment variable
    api_key = os.environ.get("CODEVF_API_KEY", "your_api_key_here")
    client = CodeVFClient(api_key=api_key)

    try:
        # Retrieve the current credit balance
        print("Fetching credit balance...")
        balance = client.credits.get_balance()

        # Interpret the returned credit balance
        available = balance.get("available")
        on_hold = balance.get("onHold")
        total = balance.get("total")

        print(f"Credit Balance Information:")
        print(f"  Available: {available}")
        print(f"  On Hold:   {on_hold}")
        print(f"  Total:     {total}")

    except Exception as e:
        print(f"Error fetching credit balance: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()

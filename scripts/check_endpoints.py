"""Ad-hoc endpoint verification script for CodeVF."""

from __future__ import annotations

from typing import Optional

from codevf import CodeVFClient, ServiceMode


API_KEY_ENV_VAR = "CODEVF_API_KEY"


def main() -> None:
    import os

    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        raise SystemExit(f"Set {API_KEY_ENV_VAR} before running this script.")

    with CodeVFClient(api_key=api_key) as client:
        project = client.projects.create(
            name="sdk-endpoint-check",
            description="Smoke validation for CodeVF endpoints",
        )
        print("Project:", project.id)

        tags = client.tags.list()
        tag_id = tags[0].id if tags else None
        print("Retrieved tags:", [tag.display_name for tag in tags])

        task = client.tasks.create(
            prompt="Verify endpoints are reachable via the SDK.",
            max_credits=15,
            project_id=project.id,
            mode=ServiceMode.STANDARD,
            tag_id=tag_id,
        )
        print("Task submitted:", task.id, "status", task.status)

        latest = client.tasks.retrieve(task.id)
        print("Latest status:", latest.status)

        cancel_payload = client.tasks.cancel(task.id)
        print("Cancel result:", cancel_payload)

        balance = client.credits.get_balance()
        print("Balance:", balance.available, balance.on_hold, balance.total)


if __name__ == "__main__":
    main()

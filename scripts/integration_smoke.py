"""Simple smoke script that exercises the core CodeVF REST endpoints through the SDK."""

from __future__ import annotations

import os
import time
from typing import Iterable, List

from codevf import CodeVFClient, ServiceMode


PROJECT_NAME = "codevf-sdk-smoke-test"
PROJECT_DESCRIPTION = "Validate SDK endpoints end-to-end."


def select_default_tag(tags: Iterable[object]) -> int:
    """Pick an active tag, preferring those named `general_purpose`."""
    for tag in tags:
        if getattr(tag, "name", None) == "general_purpose" and tag.is_active:
            return tag.id
    for tag in tags:
        if tag.is_active:
            return tag.id
    raise SystemExit("No active tags returned from /tags.")


def poll_task_until_done(client: CodeVFClient, task_id: str, attempts: int = 30, interval: float = 3.0) -> None:
    """Poll `GET /tasks/{id}` until the status transitions off of `pending/processing`."""

    for attempt in range(attempts):
        task = client.tasks.retrieve(task_id)
        print(f"[{attempt + 1}/{attempts}] Task {task.id}: {task.status}")

        if task.status.lower() in {"completed", "cancelled"}:
            if task.result and task.result.deliverables:
                names = ", ".join(item.file_name for item in task.result.deliverables)
                print(f"Deliverables: {names}")
            return

        time.sleep(interval)

    print("Reached max polling attempts without completion.")


def main() -> None:
    api_key = os.environ.get("CODEVF_API_KEY")
    if not api_key:
        raise SystemExit("Set CODEVF_API_KEY before running this script.")

    with CodeVFClient(api_key=api_key) as client:
        project = client.projects.create(name=PROJECT_NAME, description=PROJECT_DESCRIPTION)
        print(f"Project {project.name} -> ID {project.id}")

        tags = client.tags.list()
        tag_id = select_default_tag(tags)
        print(f"Using tag {tag_id} from {len(tags)} available tags.")

        print("Submitting a task to poll for completion...")
        prime_task = client.tasks.create(
            prompt="Please review the following script and suggest small cleanups.",
            max_credits=30,
            project_id=project.id,
            mode=ServiceMode.FAST,
            tag_id=tag_id,
            metadata={"environment": "smoke-test"},
            attachments=[
                {
                    "fileName": "smoke.py",
                    "mimeType": "text/x-python",
                    "content": "# smoke test\nprint('hello, world')\n",
                }
            ],
        )

        poll_task_until_done(client, prime_task.id)

        print("Submitting a second task then cancelling it...")
        cancel_task = client.tasks.create(
            prompt="This task will be cancelled immediately.",
            max_credits=5,
            project_id=project.id,
            mode=ServiceMode.STANDARD,
            tag_id=tag_id,
        )

        cancel_response = client.tasks.cancel(cancel_task.id)
        print(f"Cancel response: {cancel_response}")

        balance = client.credits.get_balance()
        print(f"Credits: available={balance.available} on_hold={balance.on_hold} total={balance.total}")


if __name__ == "__main__":
    main()

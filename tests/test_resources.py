import pytest
from unittest.mock import MagicMock

from codevf import CodeVFClient
from codevf.models.credit import CreditBalance
from codevf.models.task import TaskResponse


@pytest.fixture
def client() -> CodeVFClient:
    c = CodeVFClient(api_key="test")
    c.post = MagicMock()
    c.get = MagicMock()
    return c


def test_projects_create(client: CodeVFClient) -> None:
    client.post.return_value = {"id": 42, "name": "New Project", "createdAt": "2026-01-01T00:00:00Z"}
    project = client.projects.create(name="New Project")
    client.post.assert_called_with("projects/create", data={"name": "New Project"})
    assert project.id == 42
    assert project.name == "New Project"


def test_projects_create_with_description(client: CodeVFClient) -> None:
    client.post.return_value = {
        "id": 43,
        "name": "New Project",
        "createdAt": "2026-01-01T00:00:00Z",
        "description": "My Description",
    }
    project = client.projects.create(name="New Project", description="My Description")
    client.post.assert_called_with("projects/create", data={"name": "New Project", "description": "My Description"})
    assert project.description == "My Description"


def test_tasks_create(client: CodeVFClient) -> None:
    client.post.return_value = {
        "id": "task_123",
        "status": "pending",
        "mode": "standard",
        "maxCredits": 20,
        "createdAt": "2026-01-01T00:00:00Z",
    }

    task = client.tasks.create(prompt="Test prompt", max_credits=20, project_id=1)

    client.post.assert_called_with(
        "tasks/create",
        data={"prompt": "Test prompt", "maxCredits": 20, "projectId": 1, "mode": "standard"},
    )
    assert isinstance(task, TaskResponse)
    assert task.mode.value == "standard"


def test_tasks_create_with_attachments(client: CodeVFClient) -> None:
    client.post.return_value = {
        "id": "task_456",
        "status": "pending",
        "mode": "standard",
        "maxCredits": 50,
        "createdAt": "2026-01-01T00:00:00Z",
    }

    attachments = [
        {"fileName": "file1.txt", "mimeType": "text/plain", "content": "hello"},
        {"fileName": "file2.png", "mimeType": "image/png", "base64": "SGVsbG8="},
    ]
    client.tasks.create(prompt="Review attachments", max_credits=40, project_id=2, attachments=attachments)

    client.post.assert_called_with(
        "tasks/create",
        data={
            "prompt": "Review attachments",
            "maxCredits": 40,
            "projectId": 2,
            "mode": "standard",
            "attachments": [
                {"fileName": "file1.txt", "mimeType": "text/plain", "content": "hello"},
                {"fileName": "file2.png", "mimeType": "image/png", "content": "SGVsbG8="},
            ],
        },
    )


def test_tasks_retrieve(client: CodeVFClient) -> None:
    task_id = "task_789"
    client.get.return_value = {
        "id": task_id,
        "status": "completed",
        "mode": "fast",
        "maxCredits": 30,
        "createdAt": "2026-01-01T00:00:00Z",
        "creditsUsed": 35,
        "result": {"message": "Done", "deliverables": []},
    }

    task = client.tasks.retrieve(task_id)

    client.get.assert_called_with(f"tasks/{task_id}")
    assert isinstance(task, TaskResponse)
    assert task.status == "completed"
    assert task.credits_used == 35


def test_tasks_cancel(client: CodeVFClient) -> None:
    client.tasks.cancel("task_999")
    client.post.assert_called_with("tasks/task_999/cancel")


def test_credits_balance(client: CodeVFClient) -> None:
    client.get.return_value = {"available": 100.5, "onHold": 25.0, "total": 125.5}
    balance = client.credits.get_balance()

    client.get.assert_called_with("credits/balance")
    assert isinstance(balance, CreditBalance)
    assert balance.available == 100.5
    assert balance.on_hold == 25.0


def test_tags_list(client: CodeVFClient) -> None:
    client.get.return_value = {
        "success": True,
        "tags": [
            {
                "id": 1,
                "name": "engineer",
                "displayName": "Engineer",
                "description": None,
                "costMultiplier": "1.7",
                "isActive": True,
                "sortOrder": 1,
            }
        ],
    }

    tags = client.tags.list()

    client.get.assert_called_with("tags")
    assert len(tags) == 1
    assert tags[0].display_name == "Engineer"

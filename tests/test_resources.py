import pytest
from unittest.mock import MagicMock
from codevf import CodeVFClient

@pytest.fixture
def client() -> CodeVFClient:
    c = CodeVFClient(api_key="test")
    # We use type: ignore because mypy strict mode doesn't like assigning to methods,
    # but this is a standard pattern for mocking in tests.
    c.request = MagicMock(return_value={"ok": True})  # type: ignore[method-assign]
    return c

def test_projects_create(client: CodeVFClient) -> None:
    client.projects.create(name="New Project")
    client.request.assert_called_with("POST", "projects/create", data={"name": "New Project"})  # type: ignore[attr-defined]

def test_projects_create_with_description(client: CodeVFClient) -> None:
    client.projects.create(name="New Project", description="My Description")
    client.request.assert_called_with("POST", "projects/create", data={"name": "New Project", "description": "My Description"})  # type: ignore[attr-defined]

def test_tasks_create(client: CodeVFClient) -> None:
    client.tasks.create(prompt="Test prompt", max_credits=10, project_id=1)
    client.request.assert_called_with("POST", "tasks/create", data={  # type: ignore[attr-defined]
        "prompt": "Test prompt",
        "maxCredits": 10,
        "projectId": 1,
        "mode": "standard"
    })

def test_tasks_create_with_attachments(client: CodeVFClient) -> None:
    attachments = [
        {"fileName": "file1.txt", "mimeType": "text/plain", "content": "hello"},
        {"fileName": "file2.png", "mimeType": "image/png", "base64": "SGVsbG8="}
    ]
    client.tasks.create(
        prompt="Test with attachments",
        max_credits=20,
        project_id=1,
        attachments=attachments
    )
    client.request.assert_called_with("POST", "tasks/create", data={  # type: ignore[attr-defined]
        "prompt": "Test with attachments",
        "maxCredits": 20,
        "projectId": 1,
        "mode": "standard",
        "attachments": [
            {"fileName": "file1.txt", "mimeType": "text/plain", "content": "hello"},
            {"fileName": "file2.png", "mimeType": "image/png", "content": "SGVsbG8="}
        ]
    })

def test_tasks_retrieve(client: CodeVFClient) -> None:
    task_id = "task_123"
    mock_response = {
        "id": task_id,
        "status": "completed",
        "creditsUsed": 5,
        "result": {
            "message": "Task finished successfully",
            "deliverables": [
                {
                    "fileName": "output.txt",
                    "url": "https://example.com/output.txt",
                    "uploadedAt": "2026-01-19T10:00:00Z"
                }
            ]
        }
    }
    client.request.return_value = mock_response  # type: ignore[attr-defined]
    
    result = client.tasks.retrieve(task_id)
    
    client.request.assert_called_with("GET", f"tasks/{task_id}", params=None)  # type: ignore[attr-defined]
    assert result["id"] == task_id
    assert result["status"] == "completed"
    assert result["creditsUsed"] == 5
    assert len(result["result"]["deliverables"]) == 1
    assert result["result"]["deliverables"][0]["fileName"] == "output.txt"

def test_tasks_cancel(client: CodeVFClient) -> None:
    client.tasks.cancel("123")
    client.request.assert_called_with("POST", "tasks/123/cancel", data=None)  # type: ignore[attr-defined]

def test_credits_balance(client: CodeVFClient) -> None:
    mock_balance = {
        "available": 100.5,
        "onHold": 50.0,
        "total": 150.5
    }
    client.request.return_value = mock_balance  # type: ignore[attr-defined]
    
    # Test get_balance
    balance = client.credits.get_balance()
    client.request.assert_called_with("GET", "credits/balance", params=None)  # type: ignore[attr-defined]
    assert balance["available"] == 100.5
    assert balance["onHold"] == 50.0
    assert balance["total"] == 150.5
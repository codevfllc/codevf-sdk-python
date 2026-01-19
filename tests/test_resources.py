import pytest
from unittest.mock import MagicMock
from codevf import CodeVFClient

@pytest.fixture
def client():
    c = CodeVFClient(api_key="test")
    c.request = MagicMock(return_value={"ok": True})
    return c

def test_projects_create(client):
    client.projects.create(name="New Project")
    client.request.assert_called_with("POST", "projects/create", data={"name": "New Project"})

def test_projects_create_with_description(client):
    client.projects.create(name="New Project", description="My Description")
    client.request.assert_called_with("POST", "projects/create", data={"name": "New Project", "description": "My Description"})

def test_tasks_create(client):
    client.tasks.create(prompt="Test prompt", max_credits=10, project_id=1)
    client.request.assert_called_with("POST", "tasks/create", data={
        "prompt": "Test prompt",
        "maxCredits": 10,
        "projectId": 1,
        "mode": "standard"
    })

def test_tasks_retrieve(client):
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
    client.request.return_value = mock_response
    
    result = client.tasks.retrieve(task_id)
    
    client.request.assert_called_with("GET", f"tasks/{task_id}", params=None)
    assert result["id"] == task_id
    assert result["status"] == "completed"
    assert result["creditsUsed"] == 5
    assert len(result["result"]["deliverables"]) == 1
    assert result["result"]["deliverables"][0]["fileName"] == "output.txt"

def test_tasks_cancel(client):
    client.tasks.cancel("123")
    client.request.assert_called_with("POST", "tasks/123/cancel", data=None)

def test_credits_balance(client):
    mock_balance = {
        "available": 100.5,
        "onHold": 50.0,
        "total": 150.5
    }
    client.request.return_value = mock_balance
    
    # Test get_balance
    balance = client.credits.get_balance()
    client.request.assert_called_with("GET", "credits/balance", params=None)
    assert balance["available"] == 100.5
    assert balance["onHold"] == 50.0
    assert balance["total"] == 150.5

    # Test retrieve_balance (alias)
    balance_alias = client.credits.retrieve_balance()
    assert balance_alias == balance

def test_tags_list(client):
    client.tags.list()
    client.request.assert_called_with("GET", "tags", params=None)

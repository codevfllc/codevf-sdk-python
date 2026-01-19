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
    client.tasks.create({"description": "Task"})
    client.request.assert_called_with("POST", "tasks/create", data={"description": "Task"})

def test_tasks_retrieve(client):
    client.tasks.retrieve("123")
    client.request.assert_called_with("GET", "tasks/123", params=None)

def test_tasks_cancel(client):
    client.tasks.cancel("123")
    client.request.assert_called_with("POST", "tasks/123/cancel", data=None)

def test_credits_balance(client):
    client.credits.retrieve_balance()
    client.request.assert_called_with("GET", "credits/balance", params=None)

def test_tags_list(client):
    client.tags.list()
    client.request.assert_called_with("GET", "tags", params=None)

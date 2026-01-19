import pytest
from codevf import CodeVFClient, AuthenticationError

def test_client_init_requires_api_key(monkeypatch):
    monkeypatch.delenv("CODEVF_API_KEY", raising=False)
    with pytest.raises(AuthenticationError):
        CodeVFClient()

def test_client_init_with_arg():
    client = CodeVFClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert client.base_url == "https://codevf.com/api/v1/"

def test_client_init_with_env_var(monkeypatch):
    monkeypatch.setenv("CODEVF_API_KEY", "env_key")
    client = CodeVFClient()
    assert client.api_key == "env_key"

def test_client_base_url_normalization():
    client = CodeVFClient(api_key="test", base_url="https://api.example.com")
    assert client.base_url == "https://api.example.com/"

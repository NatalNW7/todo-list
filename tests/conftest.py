import pytest
from fastapi.testclient import TestClient

from todo_list.app import app


@pytest.fixture
def client():
    return TestClient(app)

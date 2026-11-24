import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_settings(tmp_path, api_key: str | None = None) -> Settings:
    return Settings(
        app_name="notes-api-test",
        app_env="test",
        app_version="1.2.3",
        database_path=str(tmp_path / "test.db"),
        api_key=api_key,
    )


@pytest.fixture
def client(tmp_path):
    app = create_app(make_settings(tmp_path))
    with TestClient(app) as c:
        yield c


@pytest.fixture
def secured_client(tmp_path):
    app = create_app(make_settings(tmp_path, api_key="secret"))
    with TestClient(app) as c:
        yield c

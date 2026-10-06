import os, shutil, pathlib
os.environ.update(DATABASE_PATH=":memory:", ADMIN_TOKEN="test-token", OPENAI_API_KEY="", RATE_LIMIT_PER_MIN="1000")
import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def client(tmp_path):
    kb = tmp_path / "knowledge"
    shutil.copytree(pathlib.Path(__file__).parent.parent / "knowledge", kb)
    os.environ["KNOWLEDGE_DIR"] = str(kb)
    from app.main import create_app
    with TestClient(create_app()) as c:
        yield c

import pytest
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="function", autouse=True)
def cleanup_vector_stores():
    """ベクトルストアをクリーンアップ"""
    vector_store_dir = Path("./vector_stores")
    if vector_store_dir.exists():
        shutil.rmtree(vector_store_dir)
    yield
    if vector_store_dir.exists():
        shutil.rmtree(vector_store_dir)


@pytest.fixture(scope="function")
def test_db():
    """テスト用データベース（各テストごとに新規作成）"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def test_client(test_db):
    """FastAPI TestClient"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    """テスト用ユーザー"""
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("Password123"),
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """認証ヘッダー"""
    access_token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {access_token}"}
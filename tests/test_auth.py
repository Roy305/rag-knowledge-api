"""
認証機能のテスト

ユーザー登録、ログイン、トークン検証
"""
import pytest
from fastapi import status


class TestRegister:
    """ユーザー登録のテスト"""
    
    def test_register_success(self, test_client):
        """正常: 新規ユーザー登録"""
        response = test_client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Password123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_duplicate_email(self, test_client, test_user):
        """異常: 既存のメールアドレスで登録"""
        response = test_client.post(
            "/auth/register",
            json={
                "email": test_user.email,
                "password": "Password123"
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "登録されています" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, test_client):
        """異常: 無効なメールアドレス"""
        response = test_client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "Password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_weak_password(self, test_client):
        """異常: 弱いパスワード"""
        response = test_client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """ログインのテスト"""
    
    def test_login_success(self, test_client, test_user):
        """正常: ログイン成功"""
        response = test_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "Password123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_client, test_user):
        """異常: パスワード間違い"""
        response = test_client.post(
            "/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, test_client):
        """異常: 存在しないユーザー"""
        response = test_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetMe:
    """現在のユーザー情報取得のテスト"""
    
    def test_get_me_success(self, test_client, auth_headers, test_user):
        """正常: ユーザー情報取得"""
        response = test_client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["is_active"] == test_user.is_active
    
    def test_get_me_no_token(self, test_client):
        """異常: トークンなし"""
        response = test_client.get("/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_me_invalid_token(self, test_client):
        """異常: 無効なトークン"""
        response = test_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
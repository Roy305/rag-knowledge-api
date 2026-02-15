"""ドキュメント管理機能のテスト"""
import pytest
from fastapi import status


class TestCreateDocument:
    """ドキュメント作成のテスト"""
    
    def test_create_document_success(self, test_client, auth_headers):
        """正常: ドキュメント作成"""
        response = test_client.post(
            "/documents",
            headers=auth_headers,
            json={
                "title": "テストドキュメント",
                "content": "これはテスト用のドキュメントです。"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "テストドキュメント"
        assert data["content"] == "これはテスト用のドキュメントです。"
        assert "id" in data
    
    def test_create_document_unauthorized(self, test_client):
        """異常: 認証なし"""
        response = test_client.post(
            "/documents",
            json={
                "title": "テスト",
                "content": "内容"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestListDocuments:
    """ドキュメント一覧のテスト"""
    
    def test_list_documents_empty(self, test_client, auth_headers):
        """正常: 空の一覧"""
        response = test_client.get("/documents", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_list_documents_with_data(self, test_client, auth_headers):
        """正常: ドキュメントあり"""
        # ドキュメント作成
        test_client.post(
            "/documents",
            headers=auth_headers,
            json={"title": "Doc1", "content": "Content1"}
        )
        test_client.post(
            "/documents",
            headers=auth_headers,
            json={"title": "Doc2", "content": "Content2"}
        )
        
        # 一覧取得
        response = test_client.get("/documents", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] in ["Doc1", "Doc2"]


class TestGetDocument:
    """ドキュメント詳細のテスト"""
    
    def test_get_document_success(self, test_client, auth_headers):
        """正常: ドキュメント取得"""
        # ドキュメント作成
        create_response = test_client.post(
            "/documents",
            headers=auth_headers,
            json={"title": "Test", "content": "Content"}
        )
        doc_id = create_response.json()["id"]
        
        # 詳細取得
        response = test_client.get(f"/documents/{doc_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == doc_id
        assert data["title"] == "Test"
        assert data["content"] == "Content"
    
    def test_get_document_not_found(self, test_client, auth_headers):
        """異常: 存在しないドキュメント"""
        response = test_client.get("/documents/9999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteDocument:
    """ドキュメント削除のテスト"""
    
    def test_delete_document_success(self, test_client, auth_headers):
        """正常: ドキュメント削除"""
        # ドキュメント作成
        create_response = test_client.post(
            "/documents",
            headers=auth_headers,
            json={"title": "To Delete", "content": "Will be deleted"}
        )
        doc_id = create_response.json()["id"]
        
        # 削除
        response = test_client.delete(f"/documents/{doc_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # 削除確認
        get_response = test_client.get(f"/documents/{doc_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_document_not_found(self, test_client, auth_headers):
        """異常: 存在しないドキュメント"""
        response = test_client.delete("/documents/9999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
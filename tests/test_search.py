"""RAG検索機能のテスト"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


class TestSearch:
    """RAG検索のテスト"""
    
    @patch('app.api.search.OpenAI')
    def test_search_success(self, mock_openai, test_client, auth_headers):
        """正常: RAG検索"""
        # ドキュメント作成
        test_client.post(
            "/documents",
            headers=auth_headers,
            json={
                "title": "FastAPIについて",
                "content": "FastAPIはPythonの高速なWebフレームワークです。"
            }
        )
        
        # Groq API のモック
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="FastAPIは高速なWebフレームワークです。"))
        ]
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # 検索実行
        response = test_client.post(
            "/search",
            headers=auth_headers,
            json={
                "query": "FastAPIとは？",
                "top_k": 3
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert len(data["sources"]) > 0
    
    def test_search_no_documents(self, test_client, auth_headers):
        """異常: ドキュメントなし"""
        response = test_client.post(
            "/search",
            headers=auth_headers,
            json={
                "query": "test",
                "top_k": 3
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ドキュメントがありません" in response.json()["detail"]
    
    def test_search_unauthorized(self, test_client):
        """異常: 認証なし"""
        response = test_client.post(
            "/search",
            json={
                "query": "test",
                "top_k": 3
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
"""
Testes para a API RESTful.
"""

import os
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import UploadFile


class TestAPI:
    """Testes para os endpoints da API."""
    
    def test_health_check(self, test_client):
        """Testa o endpoint de health check."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch("src.api.routes.analyze.save_uploaded_file")
    @patch("src.api.routes.analyze.registry")
    def test_analyze_endpoint(self, mock_registry, mock_save, test_client, tmp_path):
        """Testa o endpoint de análise síncrona."""
        # Mock para save_uploaded_file
        test_file_path = str(tmp_path / "test_image.jpg")
        mock_save.return_value = test_file_path
        
        # Mock para ModelContext
        mock_model_context = MagicMock()
        mock_model_context.analyze.return_value = {"test_result": "success"}
        mock_registry.create_model_context.return_value = mock_model_context
        
        # Criar arquivo de teste
        with open(test_file_path, "wb") as f:
            f.write(b"test image content")
        
        # Executar requisição com arquivo anexado
        with open(test_file_path, "rb") as test_file:
            response = test_client.post(
                "/api/analyze",
                files={"file": ("test_image.jpg", test_file, "image/jpeg")},
                params={"model_id": "test_model"}
            )
        
        # Verificar resultado
        assert response.status_code == 200
        assert "task_id" in response.json()
        assert response.json()["status"] == "completed"
        assert "test_result" in response.json()["results"]
        
        # Verificar que o modelo correto foi usado
        mock_registry.create_model_context.assert_called_once_with(
            "test_model", "latest", "tensorflow"
        )
    
    @patch("src.api.routes.analyze.save_uploaded_file")
    @patch("src.api.routes.analyze.registry")
    def test_analyze_async_endpoint(self, mock_registry, mock_save, test_client, tmp_path):
        """Testa o endpoint de análise assíncrona."""
        # Mock para save_uploaded_file
        test_file_path = str(tmp_path / "test_image.jpg")
        mock_save.return_value = test_file_path
        
        # Criar arquivo de teste
        with open(test_file_path, "wb") as f:
            f.write(b"test image content")
        
        # Executar requisição com arquivo anexado
        with open(test_file_path, "rb") as test_file:
            response = test_client.post(
                "/api/analyze/async",
                files={"file": ("test_image.jpg", test_file, "image/jpeg")},
                params={"model_id": "test_model"}
            )
        
        # Verificar resultado
        assert response.status_code == 200
        assert "task_id" in response.json()
        assert response.json()["status"] == "processing"
    
    @patch("src.api.routes.models.registry")
    def test_list_models(self, mock_registry, test_client):
        """Testa o endpoint para listar modelos."""
        # Mock para list_available_models
        mock_registry.list_available_models.return_value = [
            {"id": "model1", "version": "1.0.0"},
            {"id": "model2", "version": "2.0.0"}
        ]
        
        # Mock para get_model_metadata
        def mock_get_metadata(model_id, version):
            return {
                "id": model_id,
                "version": version,
                "task_type": "test",
                "description": "Test model"
            }
        
        mock_registry.get_model_metadata.side_effect = mock_get_metadata
        
        # Executar requisição
        response = test_client.get("/api/models")
        
        # Verificar resultado
        assert response.status_code == 200
        assert response.json()["count"] == 2
        assert len(response.json()["models"]) == 2
        assert response.json()["models"][0]["id"] == "model1"
        assert response.json()["models"][1]["id"] == "model2"
    
    @patch("src.api.routes.models.registry")
    def test_get_model_info(self, mock_registry, test_client):
        """Testa o endpoint para obter informações de um modelo."""
        # Mock para get_model_metadata
        mock_registry.get_model_metadata.return_value = {
            "id": "test_model",
            "version": "1.0.0",
            "task_type": "classification",
            "description": "Test model",
            "input_shape": [None, 224, 224, 3],
            "class_labels": ["class1", "class2"]
        }
        
        # Executar requisição
        response = test_client.get("/api/models/test_model")
        
        # Verificar resultado
        assert response.status_code == 200
        assert response.json()["id"] == "test_model"
        assert response.json()["version"] == "1.0.0"
        assert response.json()["task_type"] == "classification"

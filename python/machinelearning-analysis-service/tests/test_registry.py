"""
Testes para o registro de modelos.
"""

import pytest
from src.core.registry import ModelRegistry


class TestModelRegistry:
    """Testes para a classe ModelRegistry."""
    
    def test_singleton(self):
        """Testa que ModelRegistry é um singleton."""
        registry1 = ModelRegistry()
        registry2 = ModelRegistry()
        
        assert registry1 is registry2
    
    def test_register_model(self, mock_registry):
        """Testa registro de modelo."""
        # Mock model é registrado através do fixture
        models = mock_registry.list_available_models()
        
        assert len(models) == 1
        assert models[0]["id"] == "test_model"
        assert models[0]["version"] == "1.0.0"
    
    def test_register_context(self, mock_registry):
        """Testa registro de contexto."""
        # Mock context é registrado através do fixture
        contexts = mock_registry.list_available_contexts()
        
        assert len(contexts) == 1
        assert contexts[0] == "test_context"
    
    def test_get_model(self, mock_registry):
        """Testa obtenção de modelo pelo ID e versão."""
        model = mock_registry.get_model("test_model", "1.0.0")
        
        assert model is not None
        assert model.model_id == "test_model"
        assert model.version == "1.0.0"
    
    def test_get_model_latest(self, mock_registry):
        """Testa obtenção da versão mais recente de um modelo."""
        # Registrar outra versão do mesmo modelo
        from tests.conftest import MockModel
        newer_model = MockModel(model_id="test_model", version="2.0.0")
        mock_registry.register_model(newer_model)
        
        # Obter versão latest
        model = mock_registry.get_model("test_model", "latest")
        
        assert model is not None
        assert model.model_id == "test_model"
        assert model.version == "2.0.0"  # Deve retornar a versão mais recente
    
    def test_get_nonexistent_model(self, mock_registry):
        """Testa obtenção de modelo inexistente."""
        model = mock_registry.get_model("nonexistent_model")
        
        assert model is None
    
    def test_create_model_context(self, mock_registry):
        """Testa criação de ModelContext."""
        model_context = mock_registry.create_model_context("test_model", "1.0.0", "test_context")
        
        assert model_context is not None
        assert model_context.model.model_id == "test_model"
        assert model_context.context is not None
    
    def test_get_model_metadata(self, mock_registry):
        """Testa obtenção de metadados do modelo."""
        metadata = mock_registry.get_model_metadata("test_model", "1.0.0")
        
        assert metadata is not None
        assert metadata["id"] == "test_model"
        assert metadata["version"] == "1.0.0"
        assert "description" in metadata
        assert metadata["task_type"] == "test"

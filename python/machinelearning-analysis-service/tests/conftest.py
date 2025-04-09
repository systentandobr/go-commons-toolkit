"""
Configuração para testes automatizados.
"""

import os
import sys
import pytest
from pathlib import Path
import tempfile

# Adicionar diretório raiz ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core.registry import ModelRegistry
from src.core.context import TensorFlowContext
from src.models.generic.generic_model import GenericModel
from src.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Cliente para testes da API."""
    # Usar o TestClient do FastAPI para simular requisições HTTP
    client = TestClient(app)
    return client


@pytest.fixture
def mock_registry():
    """Registry com modelos simulados para testes."""
    # Resetar o registry para não interferir com outros testes
    ModelRegistry._instance = None
    registry = ModelRegistry()
    
    # Registrar contexto simulado
    registry.register_context("test_context", MockContext())
    
    # Registrar modelo simulado
    mock_model = MockModel(model_id="test_model", version="1.0.0")
    registry.register_model(mock_model)
    
    return registry


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


class MockContext:
    """Contexto simulado para testes."""
    
    def load_model(self, model_path):
        """Simula carregamento de modelo."""
        return {}
    
    def run_inference(self, model, inputs):
        """Simula inferência."""
        return {"test": "result"}
    
    def get_metadata(self):
        """Retorna metadados simulados."""
        return {
            "context_type": "test",
            "version": "1.0.0"
        }


class MockModel:
    """Modelo simulado para testes."""
    
    def __init__(self, model_id, version):
        self.model_id = model_id
        self.version = version
        self.metadata = {
            "description": "Modelo para testes",
            "task_type": "test",
            "input_shape": [None, 224, 224, 3],
            "class_labels": ["test_class"]
        }
    
    def preprocess(self, inputs):
        """Simula pré-processamento."""
        return inputs
    
    def predict(self, inputs):
        """Simula predição."""
        return {"test": "result"}
    
    def postprocess(self, outputs):
        """Simula pós-processamento."""
        return {
            "test_result": "success",
            "score": 0.95
        }

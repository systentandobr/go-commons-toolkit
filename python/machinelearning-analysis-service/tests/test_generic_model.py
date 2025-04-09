"""
Testes para o modelo genérico.
"""

import os
import pytest
import numpy as np
import tensorflow as tf

from src.models.generic.generic_model import GenericModel
from src.core.context import TensorFlowContext


class TestGenericModel:
    """Testes para a classe GenericModel."""
    
    def test_init(self):
        """Testa a inicialização do modelo."""
        model = GenericModel(
            model_id="test_model",
            version="1.0.0",
            model_path="test_path",
            task_type="classification",
            input_shape=[None, 224, 224, 3],
            preprocessing_config={"target_size": [224, 224]},
            postprocessing_config={"top_k": 5},
            metadata={"class_labels": ["class1", "class2"]}
        )
        
        assert model.model_id == "test_model"
        assert model.version == "1.0.0"
        assert model.model_path == "test_path"
        assert model.task_type == "classification"
        assert model.input_shape == [None, 224, 224, 3]
        assert model.preprocessing_config == {"target_size": [224, 224]}
        assert model.postprocessing_config == {"top_k": 5}
        assert model.metadata == {"class_labels": ["class1", "class2"]}
    
    def test_preprocess_image_array(self):
        """Testa o pré-processamento de imagem a partir de array."""
        model = GenericModel(
            model_id="test_model",
            version="1.0.0",
            model_path="test_path",
            task_type="classification",
            input_shape=[None, 224, 224, 3],
            preprocessing_config={"target_size": [224, 224]}
        )
        
        # Criar imagem de teste
        test_image = np.random.randint(0, 256, (100, 100, 3)).astype(np.uint8)
        
        # Pré-processar
        processed = model.preprocess(test_image)
        
        # Verificar resultado
        assert isinstance(processed, tf.Tensor)
        assert processed.shape == (1, 224, 224, 3)  # Batch de 1, redimensionado para 224x224
        assert processed.dtype == tf.float32
        assert tf.reduce_max(processed) <= 1.0  # Normalizado para [0, 1]
    
    @pytest.mark.parametrize("task_type,expected_processor", [
        ("classification", "_postprocess_classification"),
        ("detection", "_postprocess_detection"),
        ("segmentation", "_postprocess_segmentation"),
        ("video_classification", "_postprocess_video_classification"),
    ])
    def test_postprocess_dispatch(self, task_type, expected_processor, monkeypatch):
        """Testa o despacho para o processador correto conforme o tipo de tarefa."""
        model = GenericModel(
            model_id="test_model",
            version="1.0.0",
            model_path="test_path",
            task_type=task_type,
            input_shape=[None, 224, 224, 3]
        )
        
        # Mock para os métodos de pós-processamento
        called_processor = None
        
        def mock_processor(self, outputs):
            nonlocal called_processor
            called_processor = "_postprocess_classification"
            return {}
            
        def mock_detection(self, outputs):
            nonlocal called_processor
            called_processor = "_postprocess_detection"
            return {}
            
        def mock_segmentation(self, outputs):
            nonlocal called_processor
            called_processor = "_postprocess_segmentation"
            return {}
            
        def mock_video(self, outputs):
            nonlocal called_processor
            called_processor = "_postprocess_video_classification"
            return {}
        
        # Aplicar mocks
        monkeypatch.setattr(GenericModel, "_postprocess_classification", mock_processor)
        monkeypatch.setattr(GenericModel, "_postprocess_detection", mock_detection)
        monkeypatch.setattr(GenericModel, "_postprocess_segmentation", mock_segmentation)
        monkeypatch.setattr(GenericModel, "_postprocess_video_classification", mock_video)
        
        # Executar postprocess
        model.postprocess({})
        
        # Verificar que o método correto foi chamado
        assert called_processor == expected_processor
    
    def test_init_processors(self):
        """Testa a inicialização dos processadores."""
        model = GenericModel(
            model_id="test_model",
            version="1.0.0",
            model_path="test_path",
            task_type="classification",
            input_shape=[None, 224, 224, 3],
            metadata={"class_labels": ["class1", "class2"]}
        )
        
        # Verificar que os processadores foram inicializados
        assert hasattr(model, "image_processor")
        assert hasattr(model, "video_processor")
        assert hasattr(model, "post_processor")
        assert hasattr(model, "video_post_processor")

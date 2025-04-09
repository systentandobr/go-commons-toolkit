"""
Configuração do serviço de análise de machine learning.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import time

from .core.registry import ModelRegistry
from .core.context import TensorFlowContext, ONNXContext, PyTorchContext
from .models.generic.generic_model import GenericModel
from .utils.metrics import get_metrics

# Logger
logger = logging.getLogger(__name__)

# Diretório de modelos
MODELS_DIR = os.environ.get("MODELS_DIR", "models_repository")


def setup_models():
    """
    Registra modelos e contextos de execução no Registry.
    
    Esta função carrega os modelos pré-treinados, contextos de execução e os registra
    para uso pelo serviço.
    """
    logger.info("Registrando modelos e contextos")
    
    # Obter instância do registry
    registry = ModelRegistry()
    
    # Registrar contextos de execução
    registry.register_context("tensorflow", TensorFlowContext(gpu_enabled=True))
    registry.register_context("tensorflow_cpu", TensorFlowContext(gpu_enabled=False))
    
    try:
        # Tenta registrar contexto ONNX se disponível
        registry.register_context("onnx", ONNXContext())
        logger.info("Contexto ONNX registrado com sucesso")
    except ImportError:
        logger.warning("ONNX Runtime não disponível, contexto ONNX não registrado")
    
    try:
        # Tenta registrar contexto PyTorch se disponível
        registry.register_context("pytorch", PyTorchContext())
        logger.info("Contexto PyTorch registrado com sucesso")
    except ImportError:
        logger.warning("PyTorch não disponível, contexto PyTorch não registrado")
    
    # Registrar modelos genéricos para diferentes tarefas
    _register_sample_models(registry)
    
    logger.info(f"Total de modelos registrados: {len(registry.list_available_models())}")
    logger.info(f"Total de contextos registrados: {len(registry.list_available_contexts())}")


def _register_sample_models(registry):
    """
    Registra modelos de exemplo para demonstração do serviço.
    
    Em um ambiente de produção, esta função carregaria modelos reais de um
    repositório ou serviço de armazenamento.
    """
    # Modelo genérico para classificação de imagens
    generic_classifier = GenericModel(
        model_id="generic_classifier",
        version="1.0.0",
        model_path=os.path.join(MODELS_DIR, "mobilenet_v2"),
        task_type="classification",
        input_shape=[None, 224, 224, 3],
        preprocessing_config={
            "target_size": [224, 224],
            "normalize": True,
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        },
        postprocessing_config={
            "top_k": 5
        },
        metadata={
            "description": "Modelo genérico para classificação de imagens baseado em MobileNetV2",
            "class_labels": ["class1", "class2", "class3"],  # Exemplo simplificado
            "input_type": "image"
        }
    )
    registry.register_model(generic_classifier)
    
    # Modelo genérico para detecção de objetos
    generic_detector = GenericModel(
        model_id="generic_detector",
        version="1.0.0",
        model_path=os.path.join(MODELS_DIR, "ssd_mobilenet_v2"),
        task_type="detection",
        input_shape=[None, 300, 300, 3],
        preprocessing_config={
            "target_size": [300, 300],
            "normalize": True
        },
        postprocessing_config={
            "confidence_threshold": 0.5,
            "apply_nms": True,
            "iou_threshold": 0.5
        },
        metadata={
            "description": "Modelo genérico para detecção de objetos baseado em SSD MobileNetV2",
            "class_labels": ["background", "person", "car"],  # Exemplo simplificado
            "input_type": "image",
            "output_format": "ssd"
        }
    )
    registry.register_model(generic_detector)
    
    # Modelo genérico para segmentação semântica
    generic_segmenter = GenericModel(
        model_id="generic_segmenter",
        version="1.0.0",
        model_path=os.path.join(MODELS_DIR, "deeplabv3"),
        task_type="segmentation",
        input_shape=[None, 512, 512, 3],
        preprocessing_config={
            "target_size": [512, 512],
            "normalize": True
        },
        postprocessing_config={},
        metadata={
            "description": "Modelo genérico para segmentação semântica baseado em DeepLabV3",
            "class_labels": ["background", "person", "car"],  # Exemplo simplificado
            "input_type": "image"
        }
    )
    registry.register_model(generic_segmenter)
    
    # Modelo genérico para análise de vídeo
    generic_video_analyzer = GenericModel(
        model_id="generic_video_analyzer",
        version="1.0.0",
        model_path=os.path.join(MODELS_DIR, "ssd_mobilenet_v2"),
        task_type="detection",
        input_shape=[None, 300, 300, 3],
        preprocessing_config={
            "target_size": [300, 300],
            "normalize": True,
            "max_frames": 30,
            "frame_interval": 5
        },
        postprocessing_config={
            "confidence_threshold": 0.5,
            "apply_nms": True,
            "iou_threshold": 0.5
        },
        metadata={
            "description": "Modelo genérico para análise de vídeo baseado em SSD MobileNetV2",
            "class_labels": ["background", "person", "car"],  # Exemplo simplificado
            "input_type": "video",
            "output_format": "ssd"
        }
    )
    registry.register_model(generic_video_analyzer)


def setup_health_routes(app: FastAPI):
    """
    Configura rotas de health check e métricas para o serviço.
    
    Args:
        app: Aplicação FastAPI
    """
    @app.get("/health", tags=["health"])
    async def health_check():
        """
        Endpoint para verificação de saúde do serviço.
        
        Returns:
            Status de saúde do serviço
        """
        registry = ModelRegistry()
        models_count = len(registry.list_available_models())
        contexts_count = len(registry.list_available_contexts())
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - app.startup_time if hasattr(app, 'startup_time') else 0,
            "models_count": models_count,
            "contexts_count": contexts_count
        }

    @app.get("/metrics", tags=["monitoring"])
    async def metrics():
        """
        Endpoint para exportação de métricas do serviço.
        
        Returns:
            Métricas coletadas em formato JSON
        """
        return get_metrics()

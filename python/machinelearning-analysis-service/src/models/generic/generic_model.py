from typing import Any, Dict, List, Optional
import tensorflow as tf
import numpy as np
import os
from ...core.protocols import ModelProtocol
from ..base import BaseModel
from .processors import ImageProcessor, VideoProcessor
from .post_processors import (
    ClassificationPostProcessor,
    DetectionPostProcessor,
    SegmentationPostProcessor,
    VideoPostProcessor
)

class GenericModel(BaseModel[Any, Any]):
    """Modelo genérico adaptável para diferentes tarefas de análise."""
    
    def __init__(self, 
                 model_id: str, 
                 version: str,
                 model_path: str,
                 task_type: str,
                 input_shape: List[int],
                 preprocessing_config: Dict[str, Any] = None,
                 postprocessing_config: Dict[str, Any] = None,
                 metadata: Dict[str, Any] = None):
        """
        Inicializa um modelo genérico.
        
        Args:
            model_id: Identificador único do modelo
            version: Versão do modelo
            model_path: Caminho para o arquivo do modelo
            task_type: Tipo de tarefa ('classification', 'detection', 'segmentation', etc.)
            input_shape: Formato de entrada esperado pelo modelo [batch, height, width, channels]
            preprocessing_config: Configurações para pré-processamento
            postprocessing_config: Configurações para pós-processamento
            metadata: Metadados adicionais como nomes de classes, etc.
        """
        super().__init__(model_id, version)
        self.model_path = model_path
        self.task_type = task_type
        self.input_shape = input_shape
        self.preprocessing_config = preprocessing_config or {}
        self.postprocessing_config = postprocessing_config or {}
        self.metadata = metadata or {}
        self._model = None
        
        # Inicializar processadores conforme o tipo de entrada
        self._init_processors()
    
    def _init_processors(self):
        """Inicializa os processadores adequados conforme configuração."""
        # Processadores de entrada
        self.image_processor = ImageProcessor(
            target_size=self.preprocessing_config.get('target_size', self.input_shape[1:3]),
            normalize=self.preprocessing_config.get('normalize', True),
            mean=self.preprocessing_config.get('mean', None),
            std=self.preprocessing_config.get('std', None),
            add_batch_dim=self.preprocessing_config.get('add_batch_dim', True)
        )
        
        self.video_processor = VideoProcessor(
            image_processor=self.image_processor,
            max_frames=self.preprocessing_config.get('max_frames', 30),
            frame_interval=self.preprocessing_config.get('frame_interval', 1)
        )
        
        # Processadores de saída conforme o tipo de tarefa
        class_labels = self.metadata.get('class_labels', [])
        
        if self.task_type == 'classification':
            self.post_processor = ClassificationPostProcessor(
                class_labels=class_labels,
                top_k=self.postprocessing_config.get('top_k', 5)
            )
        elif self.task_type == 'detection':
            self.post_processor = DetectionPostProcessor(
                class_labels=class_labels,
                output_format=self.metadata.get('output_format', 'default'),
                confidence_threshold=self.postprocessing_config.get('confidence_threshold', 0.5),
                apply_nms=self.postprocessing_config.get('apply_nms', True),
                iou_threshold=self.postprocessing_config.get('iou_threshold', 0.5),
                max_detections=self.postprocessing_config.get('max_detections', 100)
            )
        elif self.task_type == 'segmentation':
            self.post_processor = SegmentationPostProcessor(
                class_labels=class_labels
            )
        else:
            # Processador padrão
            self.post_processor = ClassificationPostProcessor(
                class_labels=class_labels,
                top_k=self.postprocessing_config.get('top_k', 5)
            )
            
        # Processador de vídeo
        self.video_post_processor = VideoPostProcessor(
            task_type=self.task_type,
            frame_processor=self.post_processor
        )
    
    def preprocess(self, inputs: Any) -> Any:
        """Processa entrada genérica com base no tipo de tarefa."""
        # Carrega imagem de diferentes formatos
        if isinstance(inputs, str):  # Caminho do arquivo
            # Verificar se é vídeo ou imagem
            if inputs.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                return self.video_processor.process_video(inputs)
            else:  # Assumir imagem
                return self.image_processor.process_from_path(inputs)
        elif isinstance(inputs, bytes):  # Dados binários
            return self.image_processor.process_from_bytes(inputs)
        elif isinstance(inputs, np.ndarray):  # Array já carregado
            return self.image_processor.process_from_array(inputs)
        elif isinstance(inputs, list) and all(isinstance(x, (str, bytes, np.ndarray)) for x in inputs):
            # Lista de imagens/vídeos
            return [self.preprocess(x) for x in inputs]
        else:
            raise ValueError(f"Formato de entrada não suportado: {type(inputs)}")
    
    def predict(self, inputs: Any) -> Any:
        """Executa inferência baseada no tipo de entrada."""
        if self._model is None:
            raise ValueError("Modelo não carregado. Use load_model com um contexto antes.")
        
        # Lidar com diferentes tipos de entrada
        if isinstance(inputs, list) and all(isinstance(x, tf.Tensor) for x in inputs):
            # Lista de frames/imagens
            if self.metadata.get('batch_prediction', False):
                # Modelo aceita batch de entrada
                batched_inputs = tf.stack(inputs)
                return self._model(batched_inputs, training=False)
            else:
                # Predizer cada frame individualmente
                return [self._model(x, training=False) for x in inputs]
        else:
            # Imagem única
            return self._model(inputs, training=False)
    
    def postprocess(self, outputs: Any) -> Dict[str, Any]:
        """Pós-processa saídas com base no tipo de tarefa."""
        # Verificar se temos processamento de vídeo (múltiplos frames)
        if isinstance(outputs, list):
            # Processamento de vídeo
            return self.video_post_processor.process(outputs)
        else:
            # Processamento de imagem única
            return self.post_processor.process(outputs)

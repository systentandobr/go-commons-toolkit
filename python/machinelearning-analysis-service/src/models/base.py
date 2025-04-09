from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Optional
import os
import numpy as np
from ..core.protocols import ModelProtocol, ExecutionContextProtocol

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class BaseModel(ModelProtocol, Generic[InputType, OutputType], ABC):
    """Classe base para todos os modelos de ML."""
    
    def __init__(self, model_id: str, version: str):
        self.model_id = model_id
        self.version = version
        self._model = None
        self._is_loaded = False
    
    def load(self, context: ExecutionContextProtocol, model_path: Optional[str] = None) -> None:
        """Carrega o modelo usando o contexto fornecido."""
        if model_path is None and hasattr(self, 'model_path'):
            model_path = self.model_path
        
        if model_path is None:
            raise ValueError("O caminho do modelo não foi especificado")
        
        self._model = context.load_model(model_path)
        self._context = context
        self._is_loaded = True
        
        # Método opcional para pós-processamento após carregamento
        self._post_load_setup()
    
    def _post_load_setup(self) -> None:
        """Hook opcional para configuração após o carregamento do modelo."""
        pass
    
    @abstractmethod
    def preprocess(self, inputs: Any) -> InputType:
        """Implementado pelas subclasses."""
        pass
    
    @abstractmethod
    def predict(self, inputs: InputType) -> OutputType:
        """Implementado pelas subclasses."""
        pass
    
    @abstractmethod
    def postprocess(self, outputs: OutputType) -> Dict[str, Any]:
        """Implementado pelas subclasses."""
        pass
    
    @property
    def is_loaded(self) -> bool:
        """Verifica se o modelo foi carregado."""
        return self._is_loaded


class ModelContext:
    """Combina um modelo com um contexto de execução."""
    
    def __init__(self, model: ModelProtocol, context: ExecutionContextProtocol):
        self.model = model
        self.context = context
        
        # Carrega o modelo se ele tem um atributo model_path
        if hasattr(model, 'model_path') and hasattr(model, 'load'):
            model.load(context)
    
    def analyze(self, inputs: Any) -> Dict[str, Any]:
        """Executa o pipeline completo de análise."""
        # Registrar tempo de início
        import time
        start_time = time.time()
        
        # Pré-processamento
        processed_inputs = self.model.preprocess(inputs)
        preprocess_time = time.time() - start_time
        
        # Inferência
        raw_outputs = self.model.predict(processed_inputs)
        inference_time = time.time() - start_time - preprocess_time
        
        # Pós-processamento
        results = self.model.postprocess(raw_outputs)
        postprocess_time = time.time() - start_time - preprocess_time - inference_time
        
        # Adicionar metadados
        results["metadata"] = {
            "model_id": self.model.model_id,
            "model_version": self.model.version,
            "context": self.context.get_metadata(),
            "performance": {
                "preprocess_time": preprocess_time,
                "inference_time": inference_time,
                "postprocess_time": postprocess_time,
                "total_time": time.time() - start_time
            }
        }
        
        return results
    
    def get_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo e contexto."""
        return {
            "model": {
                "id": self.model.model_id,
                "version": self.model.version
            },
            "context": self.context.get_metadata()
        }

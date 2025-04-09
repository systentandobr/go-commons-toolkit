from typing import Protocol, TypeVar, Any, Dict, List
import numpy as np

T = TypeVar('T')
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class ModelProtocol(Protocol[InputType, OutputType]):
    """Protocolo para modelos de machine learning."""
    
    model_id: str
    version: str
    
    def preprocess(self, inputs: Any) -> InputType:
        """Prepara os dados para inferência."""
        ...
    
    def predict(self, inputs: InputType) -> OutputType:
        """Executa a predição no modelo."""
        ...
    
    def postprocess(self, outputs: OutputType) -> Dict[str, Any]:
        """Processa resultados da inferência para formato final."""
        ...

class ExecutionContextProtocol(Protocol):
    """Protocolo para contextos de execução."""
    
    def load_model(self, model_path: str) -> Any:
        """Carrega um modelo a partir do caminho especificado."""
        ...
    
    def run_inference(self, model: Any, inputs: Any) -> Any:
        """Executa inferência usando o modelo fornecido."""
        ...
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o contexto de execução."""
        ...

class ModelContextProtocol(Protocol):
    """Protocolo combinado que representa um modelo em um contexto de execução."""
    
    model: ModelProtocol
    context: ExecutionContextProtocol
    
    def analyze(self, inputs: Any) -> Dict[str, Any]:
        """Executa a análise completa incluindo pré, inferência e pós-processamento."""
        ...
    
    def get_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo e contexto."""
        ...

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Enum para status de tarefas."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelInfo(BaseModel):
    """Informações sobre um modelo."""
    
    id: str = Field(..., description="ID do modelo")
    version: str = Field(..., description="Versão do modelo")
    task_type: Optional[str] = Field(None, description="Tipo de tarefa do modelo")
    description: Optional[str] = Field(None, description="Descrição do modelo")
    input_shape: Optional[List[int]] = Field(None, description="Formato de entrada esperado pelo modelo")
    class_labels: Optional[List[str]] = Field(None, description="Rótulos das classes do modelo")


class ContextInfo(BaseModel):
    """Informações sobre um contexto de execução."""
    
    context_type: str = Field(..., description="Tipo de contexto (tensorflow, onnx, etc.)")
    version: str = Field(..., description="Versão do framework utilizado")
    gpu_enabled: Optional[bool] = Field(None, description="Indica se GPU está habilitada")
    gpu_available: Optional[bool] = Field(None, description="Indica se GPU está disponível")
    devices: Optional[List[str]] = Field(None, description="Dispositivos disponíveis")


class PerformanceMetrics(BaseModel):
    """Métricas de desempenho."""
    
    preprocess_time: float = Field(..., description="Tempo de pré-processamento em segundos")
    inference_time: float = Field(..., description="Tempo de inferência em segundos")
    postprocess_time: float = Field(..., description="Tempo de pós-processamento em segundos")
    total_time: float = Field(..., description="Tempo total de processamento em segundos")


class AnalysisMetadata(BaseModel):
    """Metadados da análise."""
    
    model_id: str = Field(..., description="ID do modelo utilizado")
    model_version: str = Field(..., description="Versão do modelo utilizado")
    context: ContextInfo = Field(..., description="Informações do contexto de execução")
    performance: Optional[PerformanceMetrics] = Field(None, description="Métricas de desempenho")


class AnalysisResponse(BaseModel):
    """Resposta para requisição de análise."""
    
    task_id: str = Field(..., description="ID da tarefa")
    status: TaskStatus = Field(..., description="Status da tarefa")
    results: Optional[Dict[str, Any]] = Field(None, description="Resultados da análise")
    error: Optional[str] = Field(None, description="Mensagem de erro, se houver")


class AsyncAnalysisResponse(BaseModel):
    """Resposta para requisição de análise assíncrona."""
    
    task_id: str = Field(..., description="ID da tarefa")
    status: TaskStatus = Field(..., description="Status inicial da tarefa")
    message: Optional[str] = Field(None, description="Mensagem informativa")


class BatchAnalysisResponse(BaseModel):
    """Resposta para requisição de análise em lote."""
    
    batch_id: str = Field(..., description="ID do lote")
    task_ids: List[str] = Field(..., description="Lista de IDs das tarefas individuais")
    status: TaskStatus = Field(..., description="Status do lote")
    completed_tasks: int = Field(..., description="Número de tarefas concluídas")
    total_tasks: int = Field(..., description="Número total de tarefas")


class ModelListResponse(BaseModel):
    """Resposta para listagem de modelos disponíveis."""
    
    models: List[ModelInfo] = Field(..., description="Lista de modelos disponíveis")
    count: int = Field(..., description="Número de modelos disponíveis")


class ExportResponse(BaseModel):
    """Resposta para requisição de exportação."""
    
    task_id: str = Field(..., description="ID da tarefa")
    format: str = Field(..., description="Formato de exportação")
    url: str = Field(..., description="URL para download do arquivo exportado")
    mime_type: str = Field(..., description="MIME type do arquivo exportado")

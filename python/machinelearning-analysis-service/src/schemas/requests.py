from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Modelo de requisição para análise."""
    
    model_id: str = Field(..., description="ID do modelo a ser utilizado")
    model_version: Optional[str] = Field("latest", description="Versão do modelo (default: latest)")
    context_name: Optional[str] = Field("tensorflow", description="Nome do contexto de execução")
    preprocessing_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de pré-processamento")
    postprocessing_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de pós-processamento")
    export_format: Optional[str] = Field(None, description="Formato para exportação de resultados")


class BatchAnalysisRequest(BaseModel):
    """Modelo de requisição para análise em lote."""
    
    model_id: str = Field(..., description="ID do modelo a ser utilizado")
    model_version: Optional[str] = Field("latest", description="Versão do modelo (default: latest)")
    context_name: Optional[str] = Field("tensorflow", description="Nome do contexto de execução")
    file_paths: List[str] = Field(..., min_items=1, description="Lista de caminhos para arquivos a analisar")
    preprocessing_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de pré-processamento")
    postprocessing_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros de pós-processamento")
    export_format: Optional[str] = Field(None, description="Formato para exportação de resultados")


class ImageAnalysisRequest(AnalysisRequest):
    """Modelo de requisição para análise de imagens."""
    
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Limiar de confiança para detecções")
    include_visualization: Optional[bool] = Field(False, description="Incluir visualização dos resultados")
    resize_image: Optional[bool] = Field(True, description="Redimensionar imagem de entrada para o tamanho esperado pelo modelo")


class VideoAnalysisRequest(AnalysisRequest):
    """Modelo de requisição para análise de vídeos."""
    
    max_frames: Optional[int] = Field(30, gt=0, description="Número máximo de frames a analisar")
    frame_interval: Optional[int] = Field(1, gt=0, description="Intervalo entre frames (1=todos os frames)")
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Limiar de confiança para detecções")
    include_visualization: Optional[bool] = Field(False, description="Incluir visualização dos resultados")
    temporal_aggregation: Optional[bool] = Field(True, description="Aplicar agregação temporal de resultados")


class TaskStatusRequest(BaseModel):
    """Modelo de requisição para verificar status de uma tarefa."""
    
    task_id: str = Field(..., description="ID da tarefa")

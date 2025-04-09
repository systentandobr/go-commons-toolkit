from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any, List
import uuid
import os
import asyncio
import json
import logging

from ...core.registry import ModelRegistry
from ...schemas.requests import AnalysisRequest, ImageAnalysisRequest, VideoAnalysisRequest
from ...schemas.responses import AnalysisResponse, AsyncAnalysisResponse, TaskStatus
from ...exporters import get_exporter, list_supported_formats
from ...utils.storage import save_uploaded_file, get_result_path, list_results
from ...utils.metrics import measure_time, increment_counter
from ...utils.logging import get_task_logger

# Configuração do router
router = APIRouter(prefix="/analyze", tags=["analysis"])

# Registry global
registry = ModelRegistry()

# Logger
logger = logging.getLogger(__name__)


@router.post("", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    model_id: str = "generic_detector",
    model_version: str = "latest",
    context_name: str = "tensorflow",
    confidence_threshold: Optional[float] = 0.5,
    include_visualization: Optional[bool] = False
):
    """
    Endpoint para análise síncrona de um arquivo (imagem ou vídeo).
    
    Args:
        file: Arquivo a ser analisado
        model_id: ID do modelo a utilizar
        model_version: Versão do modelo
        context_name: Nome do contexto de execução
        confidence_threshold: Limiar de confiança (0.0 a 1.0)
        include_visualization: Incluir visualização nos resultados
        
    Returns:
        Resultados da análise
    """
    # Gerar ID de tarefa
    task_id = str(uuid.uuid4())
    task_logger = get_task_logger(task_id)
    task_logger.info(f"Iniciando análise síncrona: {file.filename}")
    
    # Métricas
    increment_counter("analysis_requests", labels={"type": "sync"})
    
    # Salvar arquivo temporariamente
    with measure_time("file_upload_time"):
        file_path = await save_uploaded_file(file)
    
    try:
        # Obter modelo e contexto
        with measure_time("model_setup_time"):
            model_context = registry.create_model_context(model_id, model_version, context_name)
            
            if model_context is None:
                task_logger.error(f"Modelo {model_id}@{model_version} não encontrado")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Modelo {model_id}@{model_version} não encontrado"
                )
        
        # Modificar configurações de pós-processamento se necessário
        if hasattr(model_context.model, 'postprocessing_config'):
            model_context.model.postprocessing_config['confidence_threshold'] = confidence_threshold
        
        # Executar análise
        with measure_time("analysis_time", labels={"model_id": model_id}):
            result = model_context.analyze(file_path)
        
        # Adicionar metadados da análise
        result["task_id"] = task_id
        result["file_name"] = file.filename
        
        # Adicionar visualização se solicitado
        if include_visualization:
            # Implementação simplificada - na prática seria necessário um
            # componente dedicado para visualização
            result["visualization"] = {
                "available": False,
                "message": "Visualização não implementada nesta versão"
            }
        
        # Salvar resultado para possível uso futuro
        result_path = get_result_path(task_id, "json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        task_logger.info(f"Análise concluída com sucesso")
        
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            results=result
        )
    
    except Exception as e:
        task_logger.error(f"Erro durante análise: {str(e)}", exc_info=True)
        
        # Registrar erro
        error_data = {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
            "file_name": file.filename
        }
        
        error_path = get_result_path(task_id, "error.json")
        with open(error_path, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro durante análise: {str(e)}"
        )
    
    finally:
        # Limpar arquivo temporário
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/async", response_model=AsyncAnalysisResponse)
async def analyze_file_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_id: str = "generic_detector",
    model_version: str = "latest",
    context_name: str = "tensorflow",
    export_format: Optional[str] = None,
    confidence_threshold: Optional[float] = 0.5,
    include_visualization: Optional[bool] = False
):
    """
    Endpoint para análise assíncrona de um arquivo (imagem ou vídeo).
    
    Args:
        background_tasks: Gerenciador de tarefas em background
        file: Arquivo a ser analisado
        model_id: ID do modelo a utilizar
        model_version: Versão do modelo
        context_name: Nome do contexto de execução
        export_format: Formato para exportação de resultados
        confidence_threshold: Limiar de confiança (0.0 a 1.0)
        include_visualization: Incluir visualização nos resultados
        
    Returns:
        Informações da tarefa assíncrona
    """
    # Gerar ID de tarefa
    task_id = str(uuid.uuid4())
    task_logger = get_task_logger(task_id)
    task_logger.info(f"Iniciando análise assíncrona: {file.filename}")
    
    # Métricas
    increment_counter("analysis_requests", labels={"type": "async"})
    
    # Salvar arquivo para processamento posterior (permanente)
    file_path = await save_uploaded_file(file, permanent=True)
    
    # Adicionar tarefa de análise em background
    background_tasks.add_task(
        process_analysis_task,
        task_id=task_id,
        file_path=file_path,
        model_id=model_id,
        model_version=model_version,
        context_name=context_name,
        file_name=file.filename,
        export_format=export_format,
        confidence_threshold=confidence_threshold,
        include_visualization=include_visualization
    )
    
    return AsyncAnalysisResponse(
        task_id=task_id,
        status=TaskStatus.PROCESSING,
        message="Análise iniciada em background"
    )


@router.get("/tasks/{task_id}", response_model=AnalysisResponse)
async def get_task_result(task_id: str):
    """
    Recupera o resultado de uma tarefa de análise.
    
    Args:
        task_id: ID da tarefa
        
    Returns:
        Resultados da análise
    """
    result_path = get_result_path(task_id, "json")
    error_path = get_result_path(task_id, "error.json")
    
    if os.path.exists(result_path):
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            results=result
        )
    
    elif os.path.exists(error_path):
        with open(error_path, 'r', encoding='utf-8') as f:
            error = json.load(f)
        
        return AnalysisResponse(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error=error.get("error", "Erro desconhecido durante processamento")
        )
    
    else:
        # Verificar se há outros arquivos para esta tarefa
        task_files = list_results(task_id)
        
        if task_id in task_files:
            # Tarefa existe mas o resultado principal não está pronto
            return AnalysisResponse(
                task_id=task_id,
                status=TaskStatus.PROCESSING
            )
        else:
            # Tarefa não existe
            raise HTTPException(
                status_code=404,
                detail=f"Tarefa {task_id} não encontrada"
            )


@router.get("/tasks/{task_id}/export/{format}")
async def get_task_export(task_id: str, format: str):
    """
    Recupera uma exportação específica do resultado de uma tarefa.
    
    Args:
        task_id: ID da tarefa
        format: Formato de exportação
        
    Returns:
        Arquivo de exportação
    """
    export_path = get_result_path(task_id, format)
    
    if not os.path.exists(export_path):
        # Verificar se temos o resultado JSON e podemos exportar sob demanda
        result_path = get_result_path(task_id, "json")
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            exporter = get_exporter(format)
            if exporter:
                exporter.export(result, export_path)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Formato de exportação não suportado: {format}"
                )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Tarefa {task_id} não encontrada"
            )
    
    # Obter MIME type apropriado
    mime_types = {
        "json": "application/json",
        "csv": "text/csv",
        "parquet": "application/vnd.apache.parquet",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    
    mime_type = mime_types.get(format, "application/octet-stream")
    
    # Retornar arquivo de exportação
    return FileResponse(
        path=export_path,
        filename=f"{task_id}.{format}",
        media_type=mime_type
    )


@router.get("/formats")
async def list_export_formats():
    """
    Lista formatos de exportação suportados.
    
    Returns:
        Dicionário com formatos e MIME types
    """
    return list_supported_formats()

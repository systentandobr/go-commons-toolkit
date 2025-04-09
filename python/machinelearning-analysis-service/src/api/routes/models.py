"""
Endpoints para gerenciamento de modelos.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional, List, Dict, Any
import os
import shutil
import json
import logging

from ...core.registry import ModelRegistry
from ...schemas.responses import ModelInfo, ModelListResponse
from ...utils.metrics import measure_time, increment_counter

# Configuração do router
router = APIRouter(prefix="/models", tags=["models"])

# Registry global
registry = ModelRegistry()

# Logger
logger = logging.getLogger(__name__)

# Diretórios de modelos
MODEL_DIR = os.environ.get("MODEL_DIR", "models_repository")


@router.get("", response_model=ModelListResponse)
async def list_models():
    """
    Lista todos os modelos disponíveis.
    
    Returns:
        Lista de modelos com suas informações
    """
    with measure_time("list_models"):
        models_list = registry.list_available_models()
        
        # Converter para formato de resposta
        models_info = []
        for model in models_list:
            metadata = registry.get_model_metadata(model["id"], model["version"])
            
            models_info.append(ModelInfo(
                id=model["id"],
                version=model["version"],
                task_type=metadata.get("task_type") if metadata else None,
                description=metadata.get("description") if metadata else None,
                input_shape=metadata.get("input_shape") if metadata else None,
                class_labels=metadata.get("class_labels") if metadata else None
            ))
    
    return ModelListResponse(
        models=models_info,
        count=len(models_info)
    )


@router.get("/{model_id}", response_model=ModelInfo)
async def get_model_info(model_id: str, version: Optional[str] = "latest"):
    """
    Obtém informações detalhadas sobre um modelo específico.
    
    Args:
        model_id: ID do modelo
        version: Versão do modelo (default: latest)
        
    Returns:
        Informações detalhadas do modelo
    """
    with measure_time("get_model_info"):
        metadata = registry.get_model_metadata(model_id, version)
        
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Modelo {model_id}@{version} não encontrado"
            )
    
    return ModelInfo(
        id=metadata["id"],
        version=metadata["version"],
        task_type=metadata.get("task_type"),
        description=metadata.get("description"),
        input_shape=metadata.get("input_shape"),
        class_labels=metadata.get("class_labels")
    )


@router.get("/{model_id}/versions")
async def list_model_versions(model_id: str):
    """
    Lista todas as versões disponíveis de um modelo.
    
    Args:
        model_id: ID do modelo
        
    Returns:
        Lista de versões com metadados
    """
    with measure_time("list_model_versions"):
        models_list = registry.list_available_models()
        
        # Filtrar versões do modelo especificado
        versions = []
        for model in models_list:
            if model["id"] == model_id:
                metadata = registry.get_model_metadata(model_id, model["version"])
                
                versions.append({
                    "version": model["version"],
                    "task_type": metadata.get("task_type") if metadata else None,
                    "description": metadata.get("description") if metadata else None
                })
    
    if not versions:
        raise HTTPException(
            status_code=404,
            detail=f"Modelo {model_id} não encontrado"
        )
    
    return {
        "model_id": model_id,
        "versions": versions,
        "count": len(versions)
    }


@router.get("/contexts")
async def list_contexts():
    """
    Lista todos os contextos de execução disponíveis.
    
    Returns:
        Lista de contextos com detalhes
    """
    with measure_time("list_contexts"):
        contexts = registry.list_available_contexts()
        
        # Obter informações detalhadas de cada contexto
        contexts_info = []
        for context_name in contexts:
            context = registry.get_context(context_name)
            if context:
                contexts_info.append({
                    "name": context_name,
                    "metadata": context.get_metadata()
                })
    
    return {
        "contexts": contexts_info,
        "count": len(contexts_info)
    }

"""
Implementação de tarefas em background para o serviço de análise.
"""

import os
import json
from typing import Optional, Dict, Any
import logging

from ...core.registry import ModelRegistry
from ...exporters import get_exporter
from ...utils.storage import get_result_path
from ...utils.metrics import measure_time
from ...utils.logging import get_task_logger

# Registry global
registry = ModelRegistry()

# Logger
logger = logging.getLogger(__name__)


async def process_analysis_task(
    task_id: str,
    file_path: str,
    model_id: str,
    model_version: str,
    context_name: str,
    file_name: str,
    export_format: Optional[str] = None,
    confidence_threshold: float = 0.5,
    include_visualization: bool = False
):
    """
    Processa uma tarefa de análise em background.
    
    Args:
        task_id: ID da tarefa
        file_path: Caminho para o arquivo a analisar
        model_id: ID do modelo
        model_version: Versão do modelo
        context_name: Nome do contexto
        file_name: Nome original do arquivo
        export_format: Formato para exportação
        confidence_threshold: Limiar de confiança
        include_visualization: Incluir visualização
    """
    task_logger = get_task_logger(task_id)
    task_logger.info(f"Iniciando processamento background da tarefa {task_id}")
    
    try:
        # Obter modelo e contexto
        model_context = registry.create_model_context(model_id, model_version, context_name)
        if model_context is None:
            raise ValueError(f"Modelo {model_id}@{model_version} não encontrado")
        
        # Modificar configurações de pós-processamento se necessário
        if hasattr(model_context.model, 'postprocessing_config'):
            model_context.model.postprocessing_config['confidence_threshold'] = confidence_threshold
        
        # Executar análise
        with measure_time("analysis_time", labels={"model_id": model_id, "async": "true"}):
            result = model_context.analyze(file_path)
        
        # Adicionar metadados
        result["task_id"] = task_id
        result["file_name"] = file_name
        
        # Adicionar visualização se solicitado
        if include_visualization:
            # Implementação simplificada 
            result["visualization"] = {
                "available": False,
                "message": "Visualização não implementada nesta versão"
            }
        
        # Salvar resultados
        result_path = get_result_path(task_id, "json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Exportar em formato específico se solicitado
        if export_format:
            exporter = get_exporter(export_format)
            if exporter:
                export_path = get_result_path(task_id, export_format)
                exporter.export(result, export_path)
            else:
                task_logger.warning(f"Formato de exportação não suportado: {export_format}")
        
        task_logger.info(f"Processamento background concluído com sucesso")
    
    except Exception as e:
        task_logger.error(f"Erro durante processamento background: {str(e)}", exc_info=True)
        
        # Registrar erro
        error_data = {
            "task_id": task_id,
            "status": "failed",
            "error": str(e),
            "file_name": file_name
        }
        
        error_path = get_result_path(task_id, "error.json")
        with open(error_path, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
    
    finally:
        # Opcional: limpar arquivo de entrada após processamento
        if os.path.exists(file_path) and os.environ.get("CLEANUP_INPUT_FILES", "true").lower() == "true":
            os.remove(file_path)

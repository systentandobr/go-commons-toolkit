import os
import uuid
from pathlib import Path
import aiofiles
from fastapi import UploadFile
from typing import Dict, Any, Optional

# Diretórios padrão
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
RESULTS_DIR = os.environ.get("RESULTS_DIR", "results")


def ensure_directory(directory: str) -> None:
    """
    Garante que um diretório existe, criando-o se necessário.
    
    Args:
        directory: Caminho do diretório
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


async def save_uploaded_file(file: UploadFile, permanent: bool = False) -> str:
    """
    Salva um arquivo enviado pelo usuário.
    
    Args:
        file: Arquivo enviado
        permanent: Se True, salva em um local permanente, caso contrário em um local temporário
        
    Returns:
        Caminho para o arquivo salvo
    """
    # Definir diretório de destino
    if permanent:
        directory = UPLOAD_DIR
    else:
        # Usar diretório temporário do sistema
        directory = os.path.join(os.environ.get("TEMP_DIR", "/tmp"), "ml_analysis_uploads")
    
    # Garantir que o diretório existe
    ensure_directory(directory)
    
    # Gerar nome único para o arquivo
    file_id = str(uuid.uuid4())
    filename = file.filename
    
    # Preservar extensão do arquivo original
    if filename and "." in filename:
        extension = filename.split(".")[-1]
        save_path = os.path.join(directory, f"{file_id}.{extension}")
    else:
        save_path = os.path.join(directory, file_id)
    
    # Salvar arquivo
    async with aiofiles.open(save_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return save_path


def get_result_path(task_id: str, extension: str = "json") -> str:
    """
    Obtém o caminho para um arquivo de resultado.
    
    Args:
        task_id: ID da tarefa
        extension: Extensão do arquivo
        
    Returns:
        Caminho completo para o arquivo de resultado
    """
    # Garantir que o diretório de resultados existe
    ensure_directory(RESULTS_DIR)
    
    # Garantir que a extensão não começa com ponto
    if extension.startswith("."):
        extension = extension[1:]
    
    return os.path.join(RESULTS_DIR, f"{task_id}.{extension}")


def list_results(task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Lista arquivos de resultados disponíveis.
    
    Args:
        task_id: Se fornecido, lista apenas resultados dessa tarefa
        
    Returns:
        Dicionário com informações sobre os resultados disponíveis
    """
    ensure_directory(RESULTS_DIR)
    
    results = {}
    
    # Listar todos os arquivos no diretório de resultados
    files = os.listdir(RESULTS_DIR)
    
    for file in files:
        # Extrair task_id da parte inicial do nome do arquivo
        if "." in file:
            file_task_id, extension = file.split(".", 1)
        else:
            file_task_id, extension = file, ""
        
        # Filtrar por task_id específico se fornecido
        if task_id and file_task_id != task_id:
            continue
        
        # Adicionar ao resultado
        if file_task_id not in results:
            results[file_task_id] = []
        
        results[file_task_id].append({
            "format": extension,
            "path": os.path.join(RESULTS_DIR, file),
            "size": os.path.getsize(os.path.join(RESULTS_DIR, file)),
            "created": os.path.getctime(os.path.join(RESULTS_DIR, file))
        })
    
    return results

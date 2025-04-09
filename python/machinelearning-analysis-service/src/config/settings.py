"""
Configurações do serviço de análise de machine learning.
"""

import os
from typing import Dict, Any, List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic.
    
    Todas as configurações podem ser sobreescritas por variáveis de ambiente.
    """
    
    # Configurações básicas
    APP_NAME: str = "ML Analysis Service"
    DEBUG: bool = Field(False, env="DEBUG")
    ENV: str = Field("production", env="ENV")
    
    # Servidor
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(["*"], env="CORS_ORIGINS")
    
    # Diretórios
    UPLOAD_DIR: str = Field("uploads", env="UPLOAD_DIR")
    RESULTS_DIR: str = Field("results", env="RESULTS_DIR")
    MODELS_DIR: str = Field("models_repository", env="MODELS_DIR")
    LOGS_DIR: str = Field("logs", env="LOGS_DIR")
    TEMP_DIR: str = Field("/tmp", env="TEMP_DIR")
    
    # Configurações de log
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")
    
    # Limites
    MAX_UPLOAD_SIZE: int = Field(100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100 MB
    MAX_CONCURRENT_TASKS: int = Field(10, env="MAX_CONCURRENT_TASKS")
    TASK_TIMEOUT: int = Field(300, env="TASK_TIMEOUT")  # Segundos
    
    # TensorFlow
    TF_GPU_ENABLED: bool = Field(True, env="TF_GPU_ENABLED")
    TF_GPU_MEMORY_LIMIT: Optional[int] = Field(None, env="TF_GPU_MEMORY_LIMIT")  # MB
    TF_MIXED_PRECISION: bool = Field(False, env="TF_MIXED_PRECISION")
    
    # Limpeza
    CLEANUP_INPUT_FILES: bool = Field(True, env="CLEANUP_INPUT_FILES")
    CLEANUP_RESULTS_AFTER: int = Field(7 * 24 * 60 * 60, env="CLEANUP_RESULTS_AFTER")  # 7 dias
    
    class Config:
        """Configurações Meta do Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global das configurações
settings = Settings()


def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação.
    
    Esta função pode ser usada como dependência FastAPI para injetar as configurações.
    
    Returns:
        Instância das configurações
    """
    return settings

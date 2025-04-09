import logging
import os
import json
import yaml
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional

# Diretório de logs
LOG_DIR = os.environ.get("LOG_DIR", "logs")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


def ensure_log_directory() -> None:
    """Garante que o diretório de logs existe."""
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)


def setup_logging(config_path: Optional[str] = None) -> None:
    """
    Configura o sistema de logs.
    
    Args:
        config_path: Caminho opcional para arquivo de configuração YAML
    """
    # Garantir que o diretório de logs existe
    ensure_log_directory()
    
    # Configuração padrão
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": LOG_LEVEL,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": LOG_LEVEL,
                "formatter": "standard",
                "filename": os.path.join(LOG_DIR, "ml_analysis_service.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # Raiz
                "handlers": ["console", "file"],
                "level": LOG_LEVEL,
                "propagate": True
            }
        }
    }
    
    # Carregar configuração personalizada se fornecida
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                custom_config = yaml.safe_load(f)
            elif config_path.endswith('.json'):
                custom_config = json.load(f)
            else:
                raise ValueError(f"Formato de arquivo de configuração não suportado: {config_path}")
            
            # Mesclar com configuração padrão
            # (uma implementação completa faria merge recursivo)
            log_config.update(custom_config)
    
    # Configurar logging
    logging.config.dictConfig(log_config)
    
    # Verificar se a configuração foi aplicada
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logs inicializado")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado.
    
    Args:
        name: Nome para o logger (geralmente __name__ do módulo)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adaptador para adicionar contexto extra aos logs."""
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        """
        Inicializa o adaptador.
        
        Args:
            logger: Logger base
            extra: Informações de contexto extras
        """
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Processa a mensagem com informações de contexto.
        
        Args:
            msg: Mensagem original
            kwargs: Argumentos adicionais
            
        Returns:
            Tupla (mensagem processada, kwargs)
        """
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra'].update(self.extra)
        return msg, kwargs


def get_task_logger(task_id: str) -> logging.LoggerAdapter:
    """
    Obtém um logger especializado para tarefas.
    
    Args:
        task_id: ID da tarefa
        
    Returns:
        Logger adapter com contexto da tarefa
    """
    logger = logging.getLogger(f"task.{task_id}")
    return LoggerAdapter(logger, {"task_id": task_id})

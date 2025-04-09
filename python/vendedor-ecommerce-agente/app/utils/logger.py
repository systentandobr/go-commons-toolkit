import os
import logging
import logging.handlers
from datetime import datetime

from app.utils.config import settings

def setup_logging():
    """Configura o sistema de logs da aplicação."""
    
    # Cria o diretório de logs se não existir
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # Nome do arquivo de log com timestamp
    log_filename = os.path.join(
        settings.LOG_DIR, 
        f"{settings.APP_NAME.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    # Configuração básica de logging
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Manipulador de arquivo rotativo
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    ))
    
    # Manipulador de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Configuração do logger raiz
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Desativa loggers de bibliotecas verbosas
    for logger_name in ['asyncio', 'aiohttp', 'urllib3']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Logger específico da aplicação
    app_logger = logging.getLogger(settings.APP_NAME.lower().replace(' ', '_'))
    app_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    return app_logger

# Logger global da aplicação
logger = setup_logging()

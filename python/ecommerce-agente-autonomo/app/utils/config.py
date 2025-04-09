import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Configurações gerais
    APP_NAME: str = "E-commerce Agente Autônomo"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
    
    # Caminhos e diretórios
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")
    
    # Configurações de API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Configurações do banco de dados
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "ecommerce_agent")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_CONNECTION_STRING: str = os.getenv(
        "DB_CONNECTION_STRING", 
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Configurações do Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Configurações do Serviço WhatsApp
    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com")
    WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v17.0")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_WEBHOOK_TOKEN: str = os.getenv("WHATSAPP_WEBHOOK_TOKEN", "")
    WHATSAPP_SUPPORTS_CAROUSEL: bool = os.getenv("WHATSAPP_SUPPORTS_CAROUSEL", "False").lower() in ["true", "1", "t"]
    
    # Configurações do LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # Configurações do Serviço de E-commerce
    ECOMMERCE_API_URL: str = os.getenv("ECOMMERCE_API_URL", "http://localhost:5000/api")
    ECOMMERCE_API_TOKEN: str = os.getenv("ECOMMERCE_API_TOKEN", "")
    DEFAULT_PRODUCT_IMAGE: str = os.getenv(
        "DEFAULT_PRODUCT_IMAGE", 
        "https://via.placeholder.com/500?text=Produto"
    )
    
    # Configurações de agendamento
    EXPIRED_SESSION_CLEANUP_MINUTES: int = int(os.getenv("EXPIRED_SESSION_CLEANUP_MINUTES", "60"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    
    # Configurações de métricas
    METRICS_EXPORT_INTERVAL_SECONDS: int = int(os.getenv("METRICS_EXPORT_INTERVAL_SECONDS", "300"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Instância global de configurações
settings = Settings()

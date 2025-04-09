"""
Ponto de entrada principal para o serviço de análise de machine learning.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import api_router, LoggingMiddleware, MetricsMiddleware
from .core.registry import ModelRegistry
from .core.context import TensorFlowContext, ONNXContext, PyTorchContext
from .models.generic.generic_model import GenericModel
from .utils.logging import setup_logging
from .setup import setup_models, setup_health_routes

# Configurar logging
setup_logging()

# Logger para o módulo principal
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Machine Learning Analysis Service",
    description="Serviço para análise de imagens e vídeos usando TensorFlow",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middlewares personalizados
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Adicionar rotas da API
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Executa na inicialização do aplicativo."""
    logger.info("Iniciando serviço de análise de machine learning")
    
    # Registrar modelos e contextos
    setup_models()
    
    # Configurar rotas de health check
    setup_health_routes(app)
    
    logger.info("Serviço iniciado com sucesso")


@app.on_event("shutdown")
async def shutdown_event():
    """Executa no encerramento do aplicativo."""
    logger.info("Encerrando serviço de análise de machine learning")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Tratador de exceções HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Tratador de exceções gerais."""
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Erro interno do servidor", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    
    # Obter configurações do ambiente ou usar valores padrão
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    # Iniciar servidor
    uvicorn.run("src.main:app", host=host, port=port, reload=True)

import asyncio
import logging
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime, timedelta

from app.api.routes import router as api_router
from app.core.dependencies import get_autonomous_agent
from app.utils.logger import logger
from app.utils.config import settings

# Criação da aplicação FastAPI
app = FastAPI(
    title="E-commerce Agente Autônomo",
    description="API para um agente autônomo de vendas integrado ao WhatsApp",
    version=settings.APP_VERSION
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, isso deveria ser limitado aos domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas da API
app.include_router(api_router, prefix="/api")

# Variável para controlar o loop de tarefas agendadas
scheduled_task = None

async def scheduled_tasks():
    """Executa tarefas agendadas periodicamente."""
    try:
        agent = get_autonomous_agent()
        
        while True:
            # Executa tarefas agendadas
            logger.info("Running scheduled tasks...")
            await agent.handle_scheduled_tasks()
            
            # Aguarda o intervalo configurado
            await asyncio.sleep(settings.EXPIRED_SESSION_CLEANUP_MINUTES * 60)
    
    except asyncio.CancelledError:
        logger.info("Scheduled tasks cancelled")
    except Exception as e:
        logger.error(f"Error in scheduled tasks: {e}", exc_info=True)


@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação."""
    global scheduled_task
    
    try:
        logger.info("Starting up E-commerce Agent application...")
        
        # Inicialização de serviços...
        
        # Inicia o loop de tarefas agendadas
        scheduled_task = asyncio.create_task(scheduled_tasks())
        logger.info("Scheduled tasks started")
        
        logger.info("Application started successfully")
    
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no desligamento da aplicação."""
    global scheduled_task
    
    try:
        logger.info("Shutting down application...")
        
        # Cancela o loop de tarefas agendadas
        if scheduled_task:
            scheduled_task.cancel()
            try:
                await scheduled_task
            except asyncio.CancelledError:
                pass
        
        # Finalização de serviços...
        
        logger.info("Application shutdown complete")
    
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


@app.get("/")
async def root():
    """Endpoint raiz para verificação básica."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da aplicação."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "uptime": "unknown",  # Em uma implementação real, calcularia o uptime
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Executa a aplicação utilizando Uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

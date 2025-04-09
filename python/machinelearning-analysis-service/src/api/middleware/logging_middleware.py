import time
import logging
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Logger
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requisições e respostas.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição, registrando logs.
        
        Args:
            request: Requisição HTTP
            call_next: Próxima função na cadeia de middlewares
            
        Returns:
            Resposta HTTP
        """
        # Gerar ID de rastreamento para a requisição
        request_id = str(uuid.uuid4())
        
        # Registrar início da requisição
        start_time = time.time()
        
        # Dados básicos da requisição
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None
        }
        
        # Registrar requisição
        logger.info(f"Início de requisição: {request.method} {request.url.path}", extra=request_data)
        
        # Processar requisição
        try:
            response = await call_next(request)
            
            # Registrar sucesso
            process_time = time.time() - start_time
            response_data = {
                **request_data,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2)
            }
            
            logger.info(
                f"Requisição concluída: {request.method} {request.url.path} - Status: {response.status_code}",
                extra=response_data
            )
            
            # Adicionar headers de rastreamento
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Registrar erro
            process_time = time.time() - start_time
            error_data = {
                **request_data,
                "error": str(e),
                "process_time_ms": round(process_time * 1000, 2)
            }
            
            logger.error(
                f"Erro durante processamento: {request.method} {request.url.path} - Erro: {str(e)}",
                exc_info=True,
                extra=error_data
            )
            
            # Re-levantar exceção para tratamento pelo manipulador de exceções da aplicação
            raise

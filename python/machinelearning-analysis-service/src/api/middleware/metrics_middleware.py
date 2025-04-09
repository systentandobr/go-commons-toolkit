import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ...utils.metrics import observe_histogram, increment_counter


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para coletar métricas de requisições HTTP.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição, coletando métricas.
        
        Args:
            request: Requisição HTTP
            call_next: Próxima função na cadeia de middlewares
            
        Returns:
            Resposta HTTP
        """
        # Registrar tempo de início
        start_time = time.time()
        
        # Extrair componentes da URL para labels
        path = request.url.path
        method = request.method
        
        # Para URLs com IDs dinâmicos, substituir por placeholders
        # Ex.: /tasks/123 -> /tasks/{id}
        path_template = self._normalize_path(path)
        
        # Labels para métricas
        labels = {
            "method": method,
            "path": path_template
        }
        
        # Incrementar contador de requisições
        increment_counter("http_requests_total", labels=labels)
        
        # Processar requisição
        try:
            response = await call_next(request)
            
            # Adicionar código de status às labels
            status_labels = {**labels, "status": str(response.status_code)}
            
            # Coletar métricas de tempo de resposta
            process_time = time.time() - start_time
            observe_histogram("http_request_duration_seconds", process_time, labels=status_labels)
            
            # Incrementar contador por código de status
            increment_counter("http_responses_total", labels=status_labels)
            
            return response
            
        except Exception as e:
            # Coletar métricas para exceções
            process_time = time.time() - start_time
            error_labels = {**labels, "status": "exception", "exception": type(e).__name__}
            
            observe_histogram("http_request_duration_seconds", process_time, labels=error_labels)
            increment_counter("http_exceptions_total", labels=error_labels)
            
            raise
    
    def _normalize_path(self, path: str) -> str:
        """
        Normaliza o caminho da URL substituindo segmentos dinâmicos por placeholders.
        
        Args:
            path: Caminho da URL
            
        Returns:
            Caminho normalizado
        """
        segments = path.split('/')
        normalized = []
        
        for segment in segments:
            # Se for um segmento vazio (por exemplo, após o split de /a/b/)
            if not segment:
                normalized.append(segment)
                continue
                
            # Verificar se o segmento parece um ID (UUID, código numérico, etc.)
            if segment.isdigit() or (len(segment) > 8 and '-' in segment):
                normalized.append('{id}')
            else:
                normalized.append(segment)
        
        return '/'.join(normalized)

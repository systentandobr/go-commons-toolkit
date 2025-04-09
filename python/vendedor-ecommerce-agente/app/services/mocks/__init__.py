# Inicializador do pacote de serviços mock
from app.services.mocks.mock_user_service import MockUserService
from app.services.mocks.mock_session_service import MockSessionService
from app.services.mocks.mock_catalog_service import MockCatalogService
from app.services.mocks.mock_cart_service import MockCartService
from app.services.mocks.mock_metrics_service import MockMetricsService

__all__ = [
    'MockUserService', 
    'MockSessionService', 
    'MockCatalogService', 
    'MockCartService', 
    'MockMetricsService'
]

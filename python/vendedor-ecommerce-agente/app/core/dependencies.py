from typing import Dict, Any
import logging

from app.core.agent import AutonomousAgent
from app.services.whatsapp_service import WhatsAppService
from app.nlp.llm_manager import LLMManager
from app.persuasion.persuasion_engine import PersuasionEngine
from app.utils.logger import logger

# Instâncias globais de serviços (em uma aplicação real, usaríamos injeção de dependência apropriada)
_whatsapp_service = None
_nlp_service = None
_persuasion_service = None
_user_service = None
_session_service = None
_catalog_service = None
_cart_service = None
_metrics_service = None
_agent = None

def get_whatsapp_service():
    """Retorna uma instância do serviço WhatsApp."""
    global _whatsapp_service
    if _whatsapp_service is None:
        logger.info("Initializing WhatsApp service")
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service

def get_nlp_service():
    """Retorna uma instância do serviço NLP."""
    global _nlp_service
    if _nlp_service is None:
        logger.info("Initializing NLP service")
        _nlp_service = LLMManager()
    return _nlp_service

def get_persuasion_service():
    """Retorna uma instância do serviço de persuasão."""
    global _persuasion_service
    if _persuasion_service is None:
        logger.info("Initializing Persuasion service")
        _persuasion_service = PersuasionEngine()
    return _persuasion_service

def get_user_service():
    """Retorna uma instância do serviço de usuários."""
    global _user_service
    if _user_service is None:
        # Importação tardia para evitar dependência circular
        from app.services.mock_services import MockUserService
        logger.info("Initializing User service (mock)")
        _user_service = MockUserService()
    return _user_service

def get_session_service():
    """Retorna uma instância do serviço de sessões."""
    global _session_service
    if _session_service is None:
        # Importação tardia para evitar dependência circular
        from app.services.mock_services import MockSessionService
        logger.info("Initializing Session service (mock)")
        _session_service = MockSessionService()
    return _session_service

def get_catalog_service():
    """Retorna uma instância do serviço de catálogo."""
    global _catalog_service
    if _catalog_service is None:
        # Importação tardia para evitar dependência circular
        from app.services.mock_services import MockCatalogService
        logger.info("Initializing Catalog service (mock)")
        _catalog_service = MockCatalogService()
    return _catalog_service

def get_cart_service():
    """Retorna uma instância do serviço de carrinho."""
    global _cart_service
    if _cart_service is None:
        # Importação tardia para evitar dependência circular
        from app.services.mock_services import MockCartService
        logger.info("Initializing Cart service (mock)")
        _cart_service = MockCartService()
    return _cart_service

def get_metrics_service():
    """Retorna uma instância do serviço de métricas."""
    global _metrics_service
    if _metrics_service is None:
        # Importação tardia para evitar dependência circular
        from app.services.mock_services import MockMetricsService
        logger.info("Initializing Metrics service (mock)")
        _metrics_service = MockMetricsService()
    return _metrics_service

def get_autonomous_agent():
    """Retorna uma instância do agente autônomo."""
    global _agent
    if _agent is None:
        logger.info("Initializing Autonomous Agent")
        _agent = AutonomousAgent(
            whatsapp_service=get_whatsapp_service(),
            user_service=get_user_service(),
            session_service=get_session_service(),
            catalog_service=get_catalog_service(),
            cart_service=get_cart_service(),
            nlp_service=get_nlp_service(),
            persuasion_service=get_persuasion_service(),
            metrics_service=get_metrics_service()
        )
    return _agent

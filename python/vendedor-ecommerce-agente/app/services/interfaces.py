from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.session import Session
from app.models.interaction import Message, MessageContent, MessageDirection, MessageType

class WhatsAppServiceInterface(ABC):
    """Interface para o serviço de integração com WhatsApp."""
    
    @abstractmethod
    async def send_text_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Envia uma mensagem de texto para o número especificado."""
        pass
    
    @abstractmethod
    async def send_image_message(self, phone_number: str, image_url: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Envia uma mensagem de imagem para o número especificado."""
        pass
    
    @abstractmethod
    async def send_product_message(self, phone_number: str, products: List[Product], 
                                   caption: Optional[str] = None) -> Dict[str, Any]:
        """Envia uma mensagem com produtos para o número especificado."""
        pass
    
    @abstractmethod
    async def send_quick_reply_message(self, phone_number: str, message: str, 
                                       options: List[str]) -> Dict[str, Any]:
        """Envia uma mensagem com opções de resposta rápida."""
        pass
    
    @abstractmethod
    async def send_template_message(self, phone_number: str, template_name: str,
                                    template_params: Dict[str, Any]) -> Dict[str, Any]:
        """Envia uma mensagem usando um template pré-aprovado."""
        pass
    
    @abstractmethod
    async def process_incoming_message(self, webhook_data: Dict[str, Any]) -> Message:
        """Processa uma mensagem recebida via webhook e retorna um objeto Message."""
        pass
    
    @abstractmethod
    async def mark_message_as_read(self, message_id: str) -> bool:
        """Marca uma mensagem como lida no WhatsApp."""
        pass


class CatalogServiceInterface(ABC):
    """Interface para o serviço de catálogo de produtos."""
    
    @abstractmethod
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Obtém um produto pelo ID."""
        pass
    
    @abstractmethod
    async def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None, 
                             limit: int = 10) -> List[Product]:
        """Busca produtos de acordo com a consulta e filtros."""
        pass
    
    @abstractmethod
    async def get_products_by_category(self, category: str, filters: Optional[Dict[str, Any]] = None,
                                      limit: int = 10) -> List[Product]:
        """Obtém produtos de uma categoria específica."""
        pass
    
    @abstractmethod
    async def get_related_products(self, product_id: str, limit: int = 5) -> List[Product]:
        """Obtém produtos relacionados a um produto específico."""
        pass
    
    @abstractmethod
    async def get_popular_products(self, category: Optional[str] = None, limit: int = 10) -> List[Product]:
        """Obtém os produtos mais populares, globalmente ou por categoria."""
        pass
    
    @abstractmethod
    async def get_product_categories(self) -> List[str]:
        """Obtém a lista de categorias disponíveis."""
        pass


class CartServiceInterface(ABC):
    """Interface para o serviço de gerenciamento de carrinho."""
    
    @abstractmethod
    async def create_cart(self, user_id: str, session_id: str) -> Cart:
        """Cria um novo carrinho para o usuário."""
        pass
    
    @abstractmethod
    async def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Obtém um carrinho pelo ID."""
        pass
    
    @abstractmethod
    async def get_active_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """Obtém o carrinho ativo do usuário."""
        pass
    
    @abstractmethod
    async def add_item_to_cart(self, cart_id: str, product_id: str, quantity: int, 
                              variant_id: Optional[str] = None) -> Tuple[bool, Optional[CartItem]]:
        """Adiciona um item ao carrinho."""
        pass
    
    @abstractmethod
    async def remove_item_from_cart(self, cart_id: str, product_id: str, 
                                   variant_id: Optional[str] = None) -> bool:
        """Remove um item do carrinho."""
        pass
    
    @abstractmethod
    async def update_item_quantity(self, cart_id: str, product_id: str, quantity: int,
                                  variant_id: Optional[str] = None) -> bool:
        """Atualiza a quantidade de um item no carrinho."""
        pass
    
    @abstractmethod
    async def clear_cart(self, cart_id: str) -> bool:
        """Limpa todos os itens do carrinho."""
        pass
    
    @abstractmethod
    async def apply_promotion(self, cart_id: str, promotion_code: str) -> Tuple[bool, str]:
        """Aplica um código promocional ao carrinho."""
        pass
    
    @abstractmethod
    async def calculate_shipping(self, cart_id: str, postal_code: str) -> Dict[str, Any]:
        """Calcula opções de frete para o carrinho."""
        pass
    
    @abstractmethod
    async def generate_checkout_url(self, cart_id: str) -> Optional[str]:
        """Gera uma URL para finalização da compra."""
        pass


class UserServiceInterface(ABC):
    """Interface para o serviço de gerenciamento de usuários."""
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtém um usuário pelo ID."""
        pass
    
    @abstractmethod
    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """Obtém um usuário pelo número de telefone."""
        pass
    
    @abstractmethod
    async def create_user(self, phone: str, name: Optional[str] = None,
                         email: Optional[str] = None) -> User:
        """Cria um novo usuário."""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> Optional[User]:
        """Atualiza os dados de um usuário."""
        pass
    
    @abstractmethod
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Atualiza as preferências de um usuário."""
        pass
    
    @abstractmethod
    async def get_user_orders(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém os pedidos de um usuário."""
        pass


class SessionServiceInterface(ABC):
    """Interface para o serviço de gerenciamento de sessões."""
    
    @abstractmethod
    async def create_session(self, user_id: str, channel: str) -> Session:
        """Cria uma nova sessão para o usuário."""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Obtém uma sessão pelo ID."""
        pass
    
    @abstractmethod
    async def get_active_session_by_user(self, user_id: str, channel: str) -> Optional[Session]:
        """Obtém a sessão ativa do usuário em um determinado canal."""
        pass
    
    @abstractmethod
    async def update_session_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """Atualiza o contexto de uma sessão."""
        pass
    
    @abstractmethod
    async def close_session(self, session_id: str) -> bool:
        """Fecha uma sessão."""
        pass
    
    @abstractmethod
    async def clean_expired_sessions(self, timeout_minutes: int = 30) -> int:
        """Limpa sessões expiradas e retorna o número de sessões limpas."""
        pass


class NLPServiceInterface(ABC):
    """Interface para o serviço de processamento de linguagem natural."""
    
    @abstractmethod
    async def detect_intent(self, text: str, session_id: str, language_code: str = "pt-br") -> Dict[str, Any]:
        """Detecta a intenção em um texto."""
        pass
    
    @abstractmethod
    async def extract_entities(self, text: str, session_id: str) -> List[Dict[str, Any]]:
        """Extrai entidades de um texto."""
        pass
    
    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analisa o sentimento de um texto."""
        pass
    
    @abstractmethod
    async def generate_response(self, intent: str, entities: List[Dict[str, Any]], 
                               context: Dict[str, Any], language_code: str = "pt-br") -> str:
        """Gera uma resposta baseada na intenção, entidades e contexto."""
        pass


class PersuasionServiceInterface(ABC):
    """Interface para o serviço de técnicas de persuasão."""
    
    @abstractmethod
    async def select_technique(self, user_id: str, product_id: Optional[str], 
                              context: Dict[str, Any]) -> str:
        """Seleciona a técnica de persuasão mais adequada para o contexto."""
        pass
    
    @abstractmethod
    async def apply_technique(self, technique: str, message: str, 
                             context: Dict[str, Any]) -> str:
        """Aplica uma técnica de persuasão a uma mensagem."""
        pass
    
    @abstractmethod
    async def handle_objection(self, objection_type: str, product_id: str) -> str:
        """Gera uma resposta para lidar com uma objeção específica."""
        pass
    
    @abstractmethod
    async def track_effectiveness(self, technique: str, user_id: str, 
                                 result: bool) -> None:
        """Registra a eficácia de uma técnica para um usuário."""
        pass


class MetricsServiceInterface(ABC):
    """Interface para o serviço de métricas e análises."""
    
    @abstractmethod
    async def track_interaction(self, user_id: str, session_id: str, 
                               interaction_type: str, metadata: Dict[str, Any]) -> None:
        """Registra uma interação para análise."""
        pass
    
    @abstractmethod
    async def track_conversion(self, user_id: str, session_id: str,
                              conversion_type: str, value: float,
                              metadata: Dict[str, Any]) -> None:
        """Registra uma conversão (ex: adição ao carrinho, compra)."""
        pass
    
    @abstractmethod
    async def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Obtém métricas relacionadas a um usuário específico."""
        pass
    
    @abstractmethod
    async def get_system_metrics(self, period: str = "day") -> Dict[str, Any]:
        """Obtém métricas gerais do sistema para um período específico."""
        pass


class QueueServiceInterface(ABC):
    """Interface para o serviço de fila de atendimento."""
    
    @abstractmethod
    async def add_to_queue(self, user_id: str, session_id: str, 
                          priority: int, metadata: Dict[str, Any]) -> str:
        """Adiciona um usuário à fila de atendimento e retorna o ID do item na fila."""
        pass
    
    @abstractmethod
    async def get_queue_position(self, queue_item_id: str) -> int:
        """Obtém a posição de um item na fila."""
        pass
    
    @abstractmethod
    async def assign_next_in_queue(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Atribui o próximo item da fila a um agente."""
        pass
    
    @abstractmethod
    async def calculate_wait_time(self, queue_item_id: str) -> int:
        """Calcula o tempo estimado de espera em segundos para um item na fila."""
        pass
    
    @abstractmethod
    async def remove_from_queue(self, queue_item_id: str) -> bool:
        """Remove um item da fila."""
        pass
    
    @abstractmethod
    async def update_priority(self, queue_item_id: str, new_priority: int) -> bool:
        """Atualiza a prioridade de um item na fila."""
        pass
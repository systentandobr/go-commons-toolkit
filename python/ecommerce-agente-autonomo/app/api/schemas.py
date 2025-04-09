from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class WebhookVerificationRequest(BaseModel):
    """Modelo para verificação de webhook do WhatsApp."""
    mode: str = Field(..., alias="hub.mode")
    verify_token: str = Field(..., alias="hub.verify_token")
    challenge: str = Field(..., alias="hub.challenge")

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACTS = "contacts"
    INTERACTIVE = "interactive"

class WebhookMessage(BaseModel):
    """Modelo para mensagem recebida via webhook."""
    message_id: str
    from_number: str
    timestamp: int
    type: MessageType
    text: Optional[str] = None
    media_url: Optional[str] = None
    caption: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    interactive_type: Optional[str] = None
    interactive_id: Optional[str] = None
    interactive_title: Optional[str] = None

class ProductRecommendationRequest(BaseModel):
    """Modelo para solicitação de recomendação de produtos."""
    user_id: str
    session_id: str
    product_ids: List[str]
    intro_text: Optional[str] = "Olha só estas recomendações para você:"

class CartOperationRequest(BaseModel):
    """Modelo para operações de carrinho."""
    user_id: str
    session_id: str
    product_id: Optional[str] = None
    quantity: Optional[int] = 1
    variant_id: Optional[str] = None

class CheckoutRequest(BaseModel):
    """Modelo para solicitação de checkout."""
    user_id: str
    session_id: str
    shipping_address: Optional[Dict[str, Any]] = None
    payment_method: Optional[str] = None

class SessionCloseRequest(BaseModel):
    """Modelo para fechamento de sessão."""
    session_id: str

class HealthResponse(BaseModel):
    """Modelo para resposta de verificação de saúde."""
    status: str
    version: str
    name: str
    timestamp: datetime = Field(default_factory=datetime.now)

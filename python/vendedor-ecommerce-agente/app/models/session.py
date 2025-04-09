from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

class ConversationStage(str):
    GREETING = "greeting"
    EXPLORING = "exploring"
    PRODUCT_DETAILS = "product_details"
    CART_MANAGEMENT = "cart_management"
    CHECKOUT = "checkout"
    PAYMENT = "payment"
    ORDER_CONFIRMATION = "order_confirmation"
    SUPPORT = "support"
    CLOSING = "closing"

@dataclass
class SessionContext:
    last_intent: Optional[str] = None
    current_stage: ConversationStage = ConversationStage.GREETING
    products_viewed: List[str] = field(default_factory=list)
    last_product_id: Optional[str] = None
    last_category: Optional[str] = None
    search_query: Optional[str] = None
    cart_id: Optional[str] = None
    selected_payment_method: Optional[str] = None
    last_question: Optional[str] = None
    sentiment_trend: float = 0.0  # -1 to 1, negative to positive
    custom_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Session:
    id: str
    user_id: str
    channel: str
    started_at: datetime = field(default_factory=datetime.now)
    last_activity_at: datetime = field(default_factory=datetime.now)
    context: SessionContext = field(default_factory=SessionContext)
    is_active: bool = True
    device_info: Dict[str, Any] = field(default_factory=dict)
    
    def update_activity(self) -> None:
        self.last_activity_at = datetime.now()
    
    def set_stage(self, stage: ConversationStage) -> None:
        self.context.current_stage = stage
        self.update_activity()
    
    def add_viewed_product(self, product_id: str) -> None:
        if product_id not in self.context.products_viewed:
            self.context.products_viewed.append(product_id)
        self.context.last_product_id = product_id
        self.update_activity()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        elapsed = datetime.now() - self.last_activity_at
        return elapsed.total_seconds() / 60 > timeout_minutes

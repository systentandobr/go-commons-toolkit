from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum

class MessageDirection(str, Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    PRODUCT = "product"
    TEMPLATE = "template"
    QUICK_REPLY = "quick_reply"
    LOCATION = "location"
    DOCUMENT = "document"
    VOICE = "voice"

@dataclass
class Entity:
    type: str
    value: Any
    confidence: float

@dataclass
class MessageContent:
    text: Optional[str] = None
    media_url: Optional[str] = None
    product_ids: List[str] = field(default_factory=list)
    template_name: Optional[str] = None
    template_params: Dict[str, Any] = field(default_factory=dict)
    quick_replies: List[str] = field(default_factory=list)

@dataclass
class Message:
    id: str
    session_id: str
    user_id: str
    timestamp: datetime
    direction: MessageDirection
    type: MessageType
    content: MessageContent
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # NLP data (for incoming messages)
    intent: Optional[str] = None
    entities: List[Entity] = field(default_factory=list)
    sentiment_score: Optional[float] = None
    
    # Response data (for outgoing messages)
    response_time: Optional[float] = None
    techniques_used: List[str] = field(default_factory=list)

@dataclass
class Interaction:
    session_id: str
    user_id: str
    messages: List[Message] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_message_at: Optional[datetime] = None
    
    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        self.last_message_at = message.timestamp
    
    def get_last_message(self) -> Optional[Message]:
        if not self.messages:
            return None
        return self.messages[-1]
    
    def get_message_count(self) -> int:
        return len(self.messages)
    
    def get_duration(self) -> float:
        if not self.last_message_at:
            return 0.0
        elapsed = self.last_message_at - self.started_at
        return elapsed.total_seconds()

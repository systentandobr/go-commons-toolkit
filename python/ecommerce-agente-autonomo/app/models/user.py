from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

class CustomerTier(Enum):
    REGULAR = "regular"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

@dataclass
class UserPreferences:
    categories_of_interest: List[str] = field(default_factory=list)
    price_sensitivity: str = "medium"  # low, medium, high
    shopping_frequency: str = "occasional"  # frequent, occasional, rare
    preferred_contact_time: Optional[str] = None
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        "promotions": True,
        "order_updates": True,
        "recommendations": True
    })

@dataclass
class UserMetrics:
    lifetime_value: float = 0.0
    orders_count: int = 0
    average_order_value: float = 0.0
    cart_abandonment_rate: float = 0.0
    last_interaction: Optional[datetime] = None
    nps_score: Optional[int] = None
    conversion_rate: float = 0.0

@dataclass
class UserConsent:
    marketing: bool = False
    data_processing: bool = False
    third_party_sharing: bool = False
    last_updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class User:
    id: str
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_active_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    preferences: UserPreferences = field(default_factory=UserPreferences)
    tier: CustomerTier = CustomerTier.REGULAR
    metrics: UserMetrics = field(default_factory=UserMetrics)
    consent: UserConsent = field(default_factory=UserConsent)
    tags: List[str] = field(default_factory=list)
    
    def is_returning_customer(self) -> bool:
        return self.metrics.orders_count > 0
    
    def update_last_active(self) -> None:
        self.last_active_at = datetime.now()

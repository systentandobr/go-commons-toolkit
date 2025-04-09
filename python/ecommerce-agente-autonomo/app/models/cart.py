from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class CartStatus(Enum):
    ACTIVE = "active"
    ABANDONED = "abandoned"
    COMPLETED = "completed"
    PENDING_PAYMENT = "pending_payment"

@dataclass
class CartItem:
    product_id: str
    variant_id: Optional[str]
    name: str
    quantity: int
    unit_price: float
    total_price: float
    attributes: Dict[str, str] = field(default_factory=dict)
    added_at: datetime = field(default_factory=datetime.now)
    
    def update_quantity(self, quantity: int) -> None:
        self.quantity = quantity
        self.total_price = self.unit_price * self.quantity

@dataclass
class CartTotals:
    subtotal: float = 0.0
    shipping: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    
    @property
    def grand_total(self) -> float:
        return self.subtotal + self.shipping + self.tax - self.discount

@dataclass
class Cart:
    id: str
    user_id: str
    session_id: str
    items: List[CartItem] = field(default_factory=list)
    status: CartStatus = CartStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    totals: CartTotals = field(default_factory=CartTotals)
    applied_promotions: List[str] = field(default_factory=list)
    checkout_url: Optional[str] = None
    
    def add_item(self, item: CartItem) -> None:
        # Check if product already exists in cart
        for existing_item in self.items:
            if existing_item.product_id == item.product_id and existing_item.variant_id == item.variant_id:
                existing_item.update_quantity(existing_item.quantity + item.quantity)
                self._update_totals()
                self.updated_at = datetime.now()
                return
        
        # If not, add as new item
        self.items.append(item)
        self._update_totals()
        self.updated_at = datetime.now()
    
    def remove_item(self, product_id: str, variant_id: Optional[str] = None) -> bool:
        initial_len = len(self.items)
        self.items = [
            item for item in self.items 
            if not (item.product_id == product_id and item.variant_id == variant_id)
        ]
        if len(self.items) < initial_len:
            self._update_totals()
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_item_quantity(self, product_id: str, quantity: int, variant_id: Optional[str] = None) -> bool:
        for item in self.items:
            if item.product_id == product_id and item.variant_id == variant_id:
                if quantity <= 0:
                    return self.remove_item(product_id, variant_id)
                item.update_quantity(quantity)
                self._update_totals()
                self.updated_at = datetime.now()
                return True
        return False
    
    def clear(self) -> None:
        self.items = []
        self._update_totals()
        self.updated_at = datetime.now()
    
    def _update_totals(self) -> None:
        self.totals.subtotal = sum(item.total_price for item in self.items)
        # Other calculations can be added here (shipping, tax, etc.)

    def is_empty(self) -> bool:
        return len(self.items) == 0
    
    def get_item_count(self) -> int:
        return sum(item.quantity for item in self.items)

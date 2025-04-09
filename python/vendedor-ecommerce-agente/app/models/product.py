from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class ProductAttribute:
    name: str
    value: str
    display_name: str = ""
    
    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name.replace("_", " ").title()

@dataclass
class ProductVariant:
    id: str
    sku: str
    price: float
    attributes: Dict[str, str]
    stock: int = 0
    image_urls: List[str] = field(default_factory=list)
    is_available: bool = True

@dataclass
class Product:
    id: str
    name: str
    description: str
    category: str
    base_price: float
    image_urls: List[str] = field(default_factory=list)
    attributes: List[ProductAttribute] = field(default_factory=list)
    variants: List[ProductVariant] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    average_rating: Optional[float] = None
    reviews_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def get_display_price(self) -> str:
        return f"R${self.base_price:.2f}"
    
    def has_variants(self) -> bool:
        return len(self.variants) > 0
    
    def is_available(self) -> bool:
        if not self.has_variants():
            return True  # Assume base product is always available if no variants
        return any(variant.is_available for variant in self.variants)
    
    def get_main_image_url(self) -> Optional[str]:
        if self.image_urls:
            return self.image_urls[0]
        return None

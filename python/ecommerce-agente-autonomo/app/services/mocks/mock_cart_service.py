import uuid
import random
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from app.models.cart import Cart, CartItem, CartStatus, CartTotals
from app.services.interfaces import CartServiceInterface
from app.utils.logger import logger
from app.services.mocks.mock_catalog_service import MockCatalogService

class MockCartService(CartServiceInterface):
    """Serviço mock para gerenciamento de carrinho."""
    
    def __init__(self):
        """Inicializa o serviço com um dicionário de carrinhos em memória."""
        self.carts = {}
        self.catalog_service = MockCatalogService()  # Cria uma instância para acesso ao catálogo
    
    async def create_cart(self, user_id: str, session_id: str) -> Cart:
        """Cria um novo carrinho para o usuário."""
        # Cria um novo ID
        cart_id = f"cart_{uuid.uuid4().hex[:8]}"
        
        # Cria o novo carrinho
        cart = Cart(
            id=cart_id,
            user_id=user_id,
            session_id=session_id,
            status=CartStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            totals=CartTotals()
        )
        
        # Adiciona ao dicionário
        self.carts[cart.id] = cart
        
        logger.info(f"Created new cart: {cart.id} for user: {user_id}")
        return cart
    
    async def get_cart(self, cart_id: str) -> Optional[Cart]:
        """Obtém um carrinho pelo ID."""
        return self.carts.get(cart_id)
    
    async def get_active_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """Obtém o carrinho ativo do usuário."""
        # Encontra o carrinho ativo mais recente
        active_carts = [
            cart for cart in self.carts.values()
            if cart.user_id == user_id and cart.status == CartStatus.ACTIVE
        ]
        
        if not active_carts:
            return None
        
        # Retorna o carrinho mais recente
        return max(active_carts, key=lambda c: c.updated_at)
    
    async def add_item_to_cart(self, cart_id: str, product_id: str, quantity: int, variant_id: Optional[str] = None) -> Tuple[bool, Optional[CartItem]]:
        """Adiciona um item ao carrinho."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return False, None
        
        # Obtém o produto
        product = await self.catalog_service.get_product_by_id(product_id)
        if not product:
            return False, None
        
        # Determina o preço e outros detalhes
        price = product.base_price
        variant_info = {}
        
        # Se houver variante, atualiza o preço e informações
        if variant_id and product.has_variants():
            variant = next((v for v in product.variants if v.id == variant_id), None)
            if variant:
                price = variant.price
                variant_info = variant.attributes
            else:
                return False, None  # Variante não encontrada
        
        # Cria o item do carrinho
        cart_item = CartItem(
            product_id=product_id,
            variant_id=variant_id,
            name=product.name,
            quantity=quantity,
            unit_price=price,
            total_price=price * quantity,
            attributes=variant_info,
            added_at=datetime.now()
        )
        
        # Adiciona ao carrinho
        cart.add_item(cart_item)
        
        logger.info(f"Added item to cart: {cart.id}, product: {product_id}, quantity: {quantity}")
        return True, cart_item
    
    async def remove_item_from_cart(self, cart_id: str, product_id: str, variant_id: Optional[str] = None) -> bool:
        """Remove um item do carrinho."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return False
        
        # Remove o item
        success = cart.remove_item(product_id, variant_id)
        
        if success:
            logger.info(f"Removed item from cart: {cart.id}, product: {product_id}")
        
        return success
    
    async def update_item_quantity(self, cart_id: str, product_id: str, quantity: int, variant_id: Optional[str] = None) -> bool:
        """Atualiza a quantidade de um item no carrinho."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return False
        
        # Atualiza a quantidade
        success = cart.update_item_quantity(product_id, quantity, variant_id)
        
        if success:
            logger.info(f"Updated item quantity in cart: {cart.id}, product: {product_id}, quantity: {quantity}")
        
        return success
    
    async def clear_cart(self, cart_id: str) -> bool:
        """Limpa todos os itens do carrinho."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return False
        
        # Limpa o carrinho
        cart.clear()
        
        logger.info(f"Cleared cart: {cart.id}")
        return True
    
    async def apply_promotion(self, cart_id: str, promotion_code: str) -> Tuple[bool, str]:
        """Aplica um código promocional ao carrinho."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return False, "Carrinho não encontrado"
        
        # Códigos promocionais fictícios
        promotions = {
            "WELCOME10": {"type": "percentage", "value": 10, "message": "10% de desconto aplicado!"},
            "FRETEGRATIS": {"type": "shipping", "value": 0, "message": "Frete grátis aplicado!"},
            "OUTLET20": {"type": "percentage", "value": 20, "message": "20% de desconto aplicado!"}
        }
        
        # Verifica se o código é válido
        if promotion_code.upper() not in promotions:
            return False, "Código promocional inválido"
        
        # Obtém os detalhes da promoção
        promotion = promotions[promotion_code.upper()]
        
        # Aplica o desconto
        if promotion["type"] == "percentage":
            discount = cart.totals.subtotal * (promotion["value"] / 100)
            cart.totals.discount = discount
        elif promotion["type"] == "shipping":
            cart.totals.shipping = promotion["value"]
        
        # Adiciona a promoção à lista
        if promotion_code.upper() not in cart.applied_promotions:
            cart.applied_promotions.append(promotion_code.upper())
        
        # Atualiza o carrinho
        cart.updated_at = datetime.now()
        
        logger.info(f"Applied promotion to cart: {cart.id}, code: {promotion_code}")
        return True, promotion["message"]
    
    async def calculate_shipping(self, cart_id: str, postal_code: str) -> Dict[str, Any]:
        """Calcula opções de frete para o carrinho."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return {"error": "Carrinho não encontrado"}
        
        # Simulação de cálculo de frete
        options = []
        
        # Frete padrão
        standard_price = max(15.0, min(50.0, cart.totals.subtotal * 0.05))
        options.append({
            "type": "standard",
            "name": "Entrega Padrão",
            "price": standard_price,
            "estimated_days": random.randint(5, 10)
        })
        
        # Frete expresso
        express_price = standard_price * 2
        options.append({
            "type": "express",
            "name": "Entrega Expressa",
            "price": express_price,
            "estimated_days": random.randint(1, 3)
        })
        
        # Frete grátis para compras acima de R$300
        if cart.totals.subtotal >= 300:
            options.append({
                "type": "free",
                "name": "Frete Grátis",
                "price": 0.0,
                "estimated_days": random.randint(7, 12)
            })
        
        logger.info(f"Calculated shipping for cart: {cart.id}, postal_code: {postal_code}")
        return {
            "postal_code": postal_code,
            "options": options
        }
    
    async def generate_checkout_url(self, cart_id: str) -> Optional[str]:
        """Gera uma URL para finalização da compra."""
        cart = await self.get_cart(cart_id)
        if not cart:
            return None
        
        # Atualiza o status do carrinho
        cart.status = CartStatus.PENDING_PAYMENT
        cart.updated_at = datetime.now()
        
        # Gera uma URL fictícia
        checkout_url = f"https://loja.exemplo.com/checkout/{cart.id}?token={uuid.uuid4().hex}"
        cart.checkout_url = checkout_url
        
        logger.info(f"Generated checkout URL for cart: {cart.id}")
        return checkout_url

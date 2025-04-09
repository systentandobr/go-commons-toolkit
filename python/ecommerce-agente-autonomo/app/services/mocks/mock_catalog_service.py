import logging
from typing import Dict, Any, List, Optional

from app.models.product import Product, ProductAttribute, ProductVariant
from app.services.interfaces import CatalogServiceInterface
from app.utils.logger import logger

class MockCatalogService(CatalogServiceInterface):
    """Serviço mock para o catálogo de produtos."""
    
    def __init__(self):
        """Inicializa o serviço com um dicionário de produtos em memória."""
        self.products = {}
        self.categories = []
        self._load_mock_data()
        
    def _load_mock_data(self):
        """Carrega dados de produtos fictícios."""
        # Define categorias
        self.categories = [
            "smartphones",
            "notebooks",
            "tablets",
            "acessórios",
            "smart home",
            "áudio",
            "fotografia"
        ]
        
        # Cria produtos de exemplo
        products = [
            Product(
                id="prod1",
                name="Smartphone XYZ Pro",
                description="O mais avançado smartphone da linha XYZ, com câmera de 108MP e bateria de longa duração.",
                category="smartphones",
                base_price=3999.90,
                image_urls=["https://via.placeholder.com/500x500.png?text=Smartphone+XYZ+Pro"],
                attributes=[
                    ProductAttribute(name="processor", value="Snapdragon 8 Gen 2"),
                    ProductAttribute(name="ram", value="12GB"),
                    ProductAttribute(name="storage", value="256GB"),
                    ProductAttribute(name="screen", value="6.7 polegadas AMOLED"),
                    ProductAttribute(name="battery", value="5000mAh")
                ],
                variants=[
                    ProductVariant(
                        id="var1",
                        sku="XYZ-PRO-PRETO",
                        price=3999.90,
                        attributes={"color": "Preto"},
                        stock=15,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Smartphone+XYZ+Pro+Preto"]
                    ),
                    ProductVariant(
                        id="var2",
                        sku="XYZ-PRO-BRANCO",
                        price=3999.90,
                        attributes={"color": "Branco"},
                        stock=8,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Smartphone+XYZ+Pro+Branco"]
                    ),
                    ProductVariant(
                        id="var3",
                        sku="XYZ-PRO-AZUL",
                        price=4099.90,
                        attributes={"color": "Azul"},
                        stock=5,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Smartphone+XYZ+Pro+Azul"]
                    )
                ],
                average_rating=4.8,
                reviews_count=120,
                tags=["premium", "5G", "câmera profissional", "resistente à água"]
            ),
            Product(
                id="prod2",
                name="Notebook UltraSlim",
                description="Notebook ultrafino com processador potente e tela de alta resolução, ideal para profissionais.",
                category="notebooks",
                base_price=5499.90,
                image_urls=["https://via.placeholder.com/500x500.png?text=Notebook+UltraSlim"],
                attributes=[
                    ProductAttribute(name="processor", value="Intel Core i7"),
                    ProductAttribute(name="ram", value="16GB"),
                    ProductAttribute(name="storage", value="512GB SSD"),
                    ProductAttribute(name="screen", value="15.6 polegadas Full HD"),
                    ProductAttribute(name="battery", value="12 horas")
                ],
                variants=[
                    ProductVariant(
                        id="var4",
                        sku="ULTRA-SLIM-PRATA",
                        price=5499.90,
                        attributes={"color": "Prata"},
                        stock=10,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Notebook+UltraSlim+Prata"]
                    ),
                    ProductVariant(
                        id="var5",
                        sku="ULTRA-SLIM-GRAFITE",
                        price=5699.90,
                        attributes={"color": "Grafite"},
                        stock=7,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Notebook+UltraSlim+Grafite"]
                    )
                ],
                average_rating=4.5,
                reviews_count=45,
                tags=["ultrafino", "profissional", "alta performance"]
            ),
            Product(
                id="prod3",
                name="Fones Bluetooth SoundPro",
                description="Fones de ouvido sem fio com cancelamento de ruído e qualidade de áudio premium.",
                category="áudio",
                base_price=799.90,
                image_urls=["https://via.placeholder.com/500x500.png?text=Fones+SoundPro"],
                attributes=[
                    ProductAttribute(name="battery", value="30 horas"),
                    ProductAttribute(name="noise_cancelling", value="Ativo"),
                    ProductAttribute(name="connection", value="Bluetooth 5.2"),
                    ProductAttribute(name="microphone", value="Integrado")
                ],
                variants=[
                    ProductVariant(
                        id="var6",
                        sku="SOUND-PRO-PRETO",
                        price=799.90,
                        attributes={"color": "Preto"},
                        stock=20,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Fones+SoundPro+Preto"]
                    ),
                    ProductVariant(
                        id="var7",
                        sku="SOUND-PRO-BRANCO",
                        price=799.90,
                        attributes={"color": "Branco"},
                        stock=15,
                        image_urls=["https://via.placeholder.com/500x500.png?text=Fones+SoundPro+Branco"]
                    )
                ],
                average_rating=4.7,
                reviews_count=98,
                tags=["bluetooth", "cancelamento de ruído", "áudio premium"]
            )
        ]
        
        # Adiciona os produtos ao dicionário
        for product in products:
            self.products[product.id] = product
        
        logger.info(f"Loaded {len(self.products)} mock products in {len(self.categories)} categories")
    
    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Obtém um produto pelo ID."""
        return self.products.get(product_id)
    
    async def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> List[Product]:
        """Busca produtos de acordo com a consulta e filtros."""
        filters = filters or {}
        query = query.lower()
        
        # Filtra produtos que correspondem à consulta
        matching_products = [
            product for product in self.products.values()
            if query in product.name.lower() or
               query in product.description.lower() or
               any(query in tag.lower() for tag in product.tags) or
               query in product.category.lower()
        ]
        
        # Aplica filtros adicionais se fornecidos
        if "category" in filters:
            matching_products = [
                product for product in matching_products
                if product.category == filters["category"]
            ]
        
        if "price_min" in filters:
            matching_products = [
                product for product in matching_products
                if product.base_price >= filters["price_min"]
            ]
        
        if "price_max" in filters:
            matching_products = [
                product for product in matching_products
                if product.base_price <= filters["price_max"]
            ]
        
        # Limita o número de resultados
        return matching_products[:limit]
    
    async def get_products_by_category(self, category: str, filters: Optional[Dict[str, Any]] = None, limit: int = 10) -> List[Product]:
        """Obtém produtos de uma categoria específica."""
        filters = filters or {}
        
        # Filtra produtos da categoria
        category_products = [
            product for product in self.products.values()
            if product.category.lower() == category.lower()
        ]
        
        # Aplica filtros adicionais se fornecidos
        if "price_min" in filters:
            category_products = [
                product for product in category_products
                if product.base_price >= filters["price_min"]
            ]
        
        if "price_max" in filters:
            category_products = [
                product for product in category_products
                if product.base_price <= filters["price_max"]
            ]
        
        # Limita o número de resultados
        return category_products[:limit]
    
    async def get_related_products(self, product_id: str, limit: int = 5) -> List[Product]:
        """Obtém produtos relacionados a um produto específico."""
        product = await self.get_product_by_id(product_id)
        if not product:
            return []
        
        # Encontra produtos da mesma categoria ou com tags semelhantes
        related_products = []
        
        # Produtos da mesma categoria
        same_category = [
            p for p in self.products.values()
            if p.id != product_id and p.category == product.category
        ]
        related_products.extend(same_category)
        
        # Produtos com tags semelhantes
        for p in self.products.values():
            if p.id != product_id and p.category != product.category:
                # Conta tags em comum
                common_tags = set(p.tags).intersection(set(product.tags))
                if common_tags:
                    related_products.append(p)
        
        # Remove duplicatas, mantendo a ordem (produtos da mesma categoria primeiro)
        unique_related = []
        seen_ids = set()
        for p in related_products:
            if p.id not in seen_ids:
                unique_related.append(p)
                seen_ids.add(p.id)
        
        # Limita o número de resultados
        return unique_related[:limit]
    
    async def get_popular_products(self, category: Optional[str] = None, limit: int = 10) -> List[Product]:
        """Obtém os produtos mais populares, globalmente ou por categoria."""
        # Filtra por categoria se especificada
        if category:
            products = [p for p in self.products.values() if p.category.lower() == category.lower()]
        else:
            products = list(self.products.values())
        
        # Ordena por popularidade (usando reviews_count e rating como proxy)
        popular_products = sorted(
            products,
            key=lambda p: (p.reviews_count if p.reviews_count else 0) * (p.average_rating if p.average_rating else 0),
            reverse=True
        )
        
        # Limita o número de resultados
        return popular_products[:limit]
    
    async def get_product_categories(self) -> List[str]:
        """Obtém a lista de categorias disponíveis."""
        return self.categories

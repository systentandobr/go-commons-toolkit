import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.user import User, UserMetrics, UserPreferences, UserConsent, CustomerTier
from app.services.interfaces import UserServiceInterface
from app.utils.logger import logger

class MockUserService(UserServiceInterface):
    """Serviço mock para gerenciamento de usuários."""
    
    def __init__(self):
        """Inicializa o serviço com um dicionário de usuários em memória."""
        self.users = {}
        self._load_mock_data()
        
    def _load_mock_data(self):
        """Carrega dados de usuários fictícios."""
        # Cria alguns usuários de exemplo
        user1 = User(
            id="user1",
            phone="+5511999999991",
            name="João Silva",
            email="joao.silva@exemplo.com",
            created_at=datetime(2023, 1, 15),
            tier=CustomerTier.GOLD,
            metrics=UserMetrics(
                lifetime_value=2500.0,
                orders_count=8,
                average_order_value=312.5
            ),
            preferences=UserPreferences(
                categories_of_interest=["eletrônicos", "acessórios"],
                price_sensitivity="medium"
            )
        )
        
        user2 = User(
            id="user2",
            phone="+5511999999992",
            name="Maria Oliveira",
            email="maria.oliveira@exemplo.com",
            created_at=datetime(2023, 3, 20),
            tier=CustomerTier.SILVER,
            metrics=UserMetrics(
                lifetime_value=1200.0,
                orders_count=3,
                average_order_value=400.0
            ),
            preferences=UserPreferences(
                categories_of_interest=["moda", "casa"],
                price_sensitivity="low"
            )
        )
        
        # Adiciona os usuários ao dicionário
        self.users[user1.id] = user1
        self.users[user2.id] = user2
        self.users[user1.phone] = user1
        self.users[user2.phone] = user2
        
        logger.info(f"Loaded {len(self.users) // 2} mock users")  # Divide por 2 pois cada usuário está duplicado (ID e telefone)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtém um usuário pelo ID."""
        return self.users.get(user_id)
    
    async def get_user_by_phone(self, phone: str) -> Optional[User]:
        """Obtém um usuário pelo número de telefone."""
        return self.users.get(phone)
    
    async def create_user(self, phone: str, name: Optional[str] = None, email: Optional[str] = None) -> User:
        """Cria um novo usuário."""
        # Verifica se o usuário já existe
        existing_user = await self.get_user_by_phone(phone)
        if existing_user:
            return existing_user
        
        # Cria um novo ID
        user_id = f"user{len(self.users) // 2 + 1}"
        
        # Cria o novo usuário
        user = User(
            id=user_id,
            phone=phone,
            name=name,
            email=email,
            created_at=datetime.now(),
            last_active_at=datetime.now(),
            tier=CustomerTier.REGULAR,
            metrics=UserMetrics(),
            preferences=UserPreferences(),
            consent=UserConsent(
                data_processing=True  # Assume consentimento básico
            )
        )
        
        # Adiciona ao dicionário
        self.users[user.id] = user
        self.users[user.phone] = user
        
        logger.info(f"Created new user: {user.id} (phone: {user.phone})")
        return user
    
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> Optional[User]:
        """Atualiza os dados de um usuário."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Atualiza os campos permitidos
        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            user.email = data["email"]
        if "status" in data:
            user.status = data["status"]
        
        # Atualiza a última atividade
        user.last_active_at = datetime.now()
        
        logger.info(f"Updated user: {user.id}")
        return user
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Atualiza as preferências de um usuário."""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Atualiza as preferências
        if "categories_of_interest" in preferences:
            user.preferences.categories_of_interest = preferences["categories_of_interest"]
        if "price_sensitivity" in preferences:
            user.preferences.price_sensitivity = preferences["price_sensitivity"]
        if "shopping_frequency" in preferences:
            user.preferences.shopping_frequency = preferences["shopping_frequency"]
        if "preferred_contact_time" in preferences:
            user.preferences.preferred_contact_time = preferences["preferred_contact_time"]
        if "notification_preferences" in preferences:
            user.preferences.notification_preferences.update(preferences["notification_preferences"])
        
        logger.info(f"Updated preferences for user: {user.id}")
        return True
    
    async def get_user_orders(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém os pedidos de um usuário."""
        import random
        
        user = await self.get_user_by_id(user_id)
        if not user:
            return []
        
        # Gera pedidos fictícios com base nas métricas do usuário
        orders = []
        for i in range(min(user.metrics.orders_count, limit)):
            order_date = datetime.now()
            order_date = order_date.replace(
                day=max(1, order_date.day - i * 15),
                hour=random.randint(8, 20),
                minute=random.randint(0, 59)
            )
            
            orders.append({
                "id": f"order{user_id[-1]}{i+1}",
                "date": order_date.isoformat(),
                "total": round(user.metrics.average_order_value * (0.8 + random.random() * 0.4), 2),
                "status": random.choice(["delivered", "processing", "shipped"]),
                "items_count": random.randint(1, 5)
            })
        
        return orders

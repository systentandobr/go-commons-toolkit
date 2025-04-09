import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import uuid

from app.models.session import Session, ConversationStage
from app.models.user import User
from app.models.interaction import Message, MessageContent, MessageDirection, MessageType, Interaction
from app.utils.logger import logger

class ConversationManager:
    """
    Gerenciador de conversações para o agente autônomo.
    Responsável por manter o estado da conversa e gerenciar o fluxo de diálogo.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de conversações."""
        # Cache de conversas ativas (em um sistema real, seria armazenado em Redis)
        self._active_conversations: Dict[str, Dict[str, Any]] = {}
    
    def create_conversation(self, user: User, session: Session) -> str:
        """Cria uma nova conversa e retorna o ID da conversa."""
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        # Cria o objeto de conversa
        conversation = {
            "id": conversation_id,
            "user_id": user.id,
            "session_id": session.id,
            "created_at": datetime.now(),
            "last_updated_at": datetime.now(),
            "messages": [],
            "current_stage": session.context.current_stage,
            "topic": None,
            "last_intent": None,
            "active_products": [],
            "flow_state": {},
            "is_active": True
        }
        
        # Adiciona ao cache
        self._active_conversations[conversation_id] = conversation
        
        logger.info(f"Created new conversation: {conversation_id} for user: {user.id}")
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma conversa pelo ID."""
        return self._active_conversations.get(conversation_id)
    
    def get_conversation_by_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma conversa pela sessão."""
        for conversation in self._active_conversations.values():
            if conversation["session_id"] == session_id and conversation["is_active"]:
                return conversation
        return None
    
    def add_message(self, conversation_id: str, message: Message) -> bool:
        """Adiciona uma mensagem à conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Adiciona a mensagem
        conversation["messages"].append(message)
        
        # Atualiza o timestamp
        conversation["last_updated_at"] = datetime.now()
        
        # Atualiza o último intent se for uma mensagem do usuário
        if message.direction == MessageDirection.INCOMING and message.intent:
            conversation["last_intent"] = message.intent
        
        logger.info(f"Added message to conversation: {conversation_id}")
        return True
    
    def update_stage(self, conversation_id: str, stage: ConversationStage) -> bool:
        """Atualiza o estágio da conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Atualiza o estágio
        conversation["current_stage"] = stage
        
        # Atualiza o timestamp
        conversation["last_updated_at"] = datetime.now()
        
        logger.info(f"Updated stage of conversation: {conversation_id} to {stage}")
        return True
    
    def update_flow_state(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza o estado do fluxo da conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Atualiza o estado do fluxo
        conversation["flow_state"].update(updates)
        
        # Atualiza o timestamp
        conversation["last_updated_at"] = datetime.now()
        
        logger.info(f"Updated flow state of conversation: {conversation_id}")
        return True
    
    def add_active_product(self, conversation_id: str, product_id: str) -> bool:
        """Adiciona um produto ativo à conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Adiciona o produto aos produtos ativos
        if product_id not in conversation["active_products"]:
            conversation["active_products"].append(product_id)
        
        # Limita a 5 produtos ativos
        if len(conversation["active_products"]) > 5:
            conversation["active_products"] = conversation["active_products"][-5:]
        
        # Atualiza o timestamp
        conversation["last_updated_at"] = datetime.now()
        
        logger.info(f"Added active product {product_id} to conversation: {conversation_id}")
        return True
    
    def set_topic(self, conversation_id: str, topic: str) -> bool:
        """Define o tópico da conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Define o tópico
        conversation["topic"] = topic
        
        # Atualiza o timestamp
        conversation["last_updated_at"] = datetime.now()
        
        logger.info(f"Set topic of conversation: {conversation_id} to {topic}")
        return True
    
    def close_conversation(self, conversation_id: str) -> bool:
        """Fecha uma conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Marca como inativa
        conversation["is_active"] = False
        
        # Atualiza o timestamp
        conversation["last_updated_at"] = datetime.now()
        
        logger.info(f"Closed conversation: {conversation_id}")
        return True
    
    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Message]:
        """Obtém o histórico de mensagens da conversa."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        # Retorna as últimas 'limit' mensagens
        return conversation["messages"][-limit:]
    
    def get_recent_messages(self, conversation_id: str, message_count: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém as mensagens recentes da conversa em um formato adequado para o LLM.
        Retorna uma lista de dicionários no formato {"role": "user"|"assistant", "content": "mensagem"}.
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        recent_messages = []
        for message in conversation["messages"][-message_count:]:
            role = "user" if message.direction == MessageDirection.INCOMING else "assistant"
            content = message.content.text or "[IMAGEM]" if message.type == MessageType.IMAGE else "[CONTEÚDO NÃO TEXTUAL]"
            
            recent_messages.append({
                "role": role,
                "content": content
            })
        
        return recent_messages
    
    def get_suggested_products(self, conversation_id: str) -> List[str]:
        """Obtém os produtos sugeridos na conversa atual."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        # Busca nas mensagens do agente por produtos mostrados
        suggested_products = []
        for message in conversation["messages"]:
            if message.direction == MessageDirection.OUTGOING and message.content.product_ids:
                suggested_products.extend(message.content.product_ids)
        
        # Remove duplicatas mantendo a ordem
        unique_products = []
        for product_id in suggested_products:
            if product_id not in unique_products:
                unique_products.append(product_id)
        
        return unique_products
    
    def clean_expired_conversations(self, inactive_minutes: int = 60) -> int:
        """Limpa conversas inativas há mais de 'inactive_minutes' minutos."""
        now = datetime.now()
        expired_count = 0
        
        for conversation_id, conversation in list(self._active_conversations.items()):
            # Calcula a diferença de tempo
            last_updated = conversation["last_updated_at"]
            minutes_inactive = (now - last_updated).total_seconds() / 60
            
            # Marca como inativa se expirou
            if minutes_inactive > inactive_minutes and conversation["is_active"]:
                conversation["is_active"] = False
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned {expired_count} expired conversations")
        
        return expired_count

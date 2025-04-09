import uuid
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from app.models.user import User
from app.models.session import Session, ConversationStage
from app.models.interaction import Message, MessageContent, MessageType, MessageDirection, Interaction
from app.models.cart import Cart, CartItem

from app.services.interfaces import (
    WhatsAppServiceInterface,
    UserServiceInterface,
    SessionServiceInterface,
    CatalogServiceInterface,
    CartServiceInterface,
    NLPServiceInterface,
    PersuasionServiceInterface,
    MetricsServiceInterface
)

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """
    Agente autônomo principal que gerencia as interações com os usuários.
    Responsável por coordenar os diversos serviços e processar as mensagens.
    """
    
    def __init__(
        self,
        whatsapp_service: WhatsAppServiceInterface,
        user_service: UserServiceInterface,
        session_service: SessionServiceInterface,
        catalog_service: CatalogServiceInterface,
        cart_service: CartServiceInterface,
        nlp_service: NLPServiceInterface,
        persuasion_service: PersuasionServiceInterface,
        metrics_service: MetricsServiceInterface
    ):
        self.whatsapp_service = whatsapp_service
        self.user_service = user_service
        self.session_service = session_service
        self.catalog_service = catalog_service
        self.cart_service = cart_service
        self.nlp_service = nlp_service
        self.persuasion_service = persuasion_service
        self.metrics_service = metrics_service
        
        # Cache em memória para sessões ativas (em um sistema real, seria armazenado em Redis)
        self._active_sessions: Dict[str, Session] = {}
        self._active_interactions: Dict[str, Interaction] = {}
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um webhook recebido do WhatsApp e retorna a resposta."""
        try:
            # Processa a mensagem recebida
            incoming_message = await self.whatsapp_service.process_incoming_message(webhook_data)
            
            # Marca a mensagem como lida
            await self.whatsapp_service.mark_message_as_read(incoming_message.id)
            
            # Obtém ou cria o usuário
            user = await self._get_or_create_user(incoming_message.metadata["phone_number"])
            
            # Obtém ou cria a sessão
            session = await self._get_or_create_session(user.id, "whatsapp")
            
            # Atualiza os IDs na mensagem
            incoming_message.user_id = user.id
            incoming_message.session_id = session.id
            
            # Processa a mensagem e gera uma resposta
            await self._process_message(user, session, incoming_message)
            
            return {"status": "success"}
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    async def _get_or_create_user(self, phone_number: str) -> User:
        """Obtém um usuário existente ou cria um novo se não existir."""
        user = await self.user_service.get_user_by_phone(phone_number)
        
        if not user:
            # Cria um novo usuário
            user = await self.user_service.create_user(phone=phone_number)
            logger.info(f"Created new user with ID {user.id} for phone {phone_number}")
        else:
            # Atualiza a última atividade do usuário
            user.update_last_active()
            # Em uma implementação real, salvaria as mudanças no banco de dados
        
        return user
    
    async def _get_or_create_session(self, user_id: str, channel: str) -> Session:
        """Obtém uma sessão ativa ou cria uma nova se não existir."""
        # Verifica o cache primeiro
        for session in self._active_sessions.values():
            if session.user_id == user_id and session.channel == channel and not session.is_expired():
                return session
        
        # Verifica no banco de dados
        session = await self.session_service.get_active_session_by_user(user_id, channel)
        
        if not session or session.is_expired():
            # Cria uma nova sessão
            session = await self.session_service.create_session(user_id, channel)
            logger.info(f"Created new session with ID {session.id} for user {user_id}")
        
        # Adiciona ao cache
        self._active_sessions[session.id] = session
        return session
    
    async def _process_message(self, user: User, session: Session, message: Message) -> None:
        """Processa uma mensagem recebida e envia uma resposta adequada."""
        start_time = datetime.now()
        
        # Adiciona a mensagem à interação atual
        interaction = self._get_or_create_interaction(session.id, user.id)
        interaction.add_message(message)
        
        # Detecta a intenção e entidades
        intent_data = await self.nlp_service.detect_intent(message.content.text or "", session.id)
        entities_data = await self.nlp_service.extract_entities(message.content.text or "", session.id)
        
        # Atualiza a mensagem com os dados de NLP
        message.intent = intent_data.get("intent")
        message.entities = [
            {
                "type": entity["type"],
                "value": entity["value"],
                "confidence": entity["confidence"]
            }
            for entity in entities_data
        ]
        
        # Analisa o sentimento
        sentiment_data = await self.nlp_service.analyze_sentiment(message.content.text or "")
        message.sentiment_score = sentiment_data.get("score", 0.0)
        
        # Atualiza o contexto da sessão
        await self._update_session_context(session, message)
        
        # Seleciona a técnica de persuasão adequada se relevante
        persuasion_technique = None
        product_id = session.context.last_product_id
        if product_id or session.context.current_stage in [
            ConversationStage.EXPLORING, 
            ConversationStage.PRODUCT_DETAILS,
            ConversationStage.CHECKOUT
        ]:
            persuasion_technique = await self.persuasion_service.select_technique(
                user.id, 
                product_id,
                {
                    "intent": message.intent,
                    "stage": session.context.current_stage,
                    "sentiment": message.sentiment_score
                }
            )
        
        # Gera a resposta
        response_text = await self._generate_response(user, session, message, persuasion_technique)
        
        # Aplica a técnica de persuasão se selecionada
        if persuasion_technique:
            response_text = await self.persuasion_service.apply_technique(
                persuasion_technique,
                response_text,
                {
                    "user_id": user.id,
                    "product_id": product_id,
                    "stage": session.context.current_stage
                }
            )
        
        # Cria e envia a resposta
        await self._send_response(user, session, response_text, persuasion_technique)
        
        # Calcula o tempo de resposta
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Registra as métricas da interação
        await self.metrics_service.track_interaction(
            user_id=user.id,
            session_id=session.id,
            interaction_type="message_processed",
            metadata={
                "intent": message.intent,
                "sentiment": message.sentiment_score,
                "response_time": response_time,
                "stage": session.context.current_stage,
                "persuasion_technique": persuasion_technique
            }
        )
    
    def _get_or_create_interaction(self, session_id: str, user_id: str) -> Interaction:
        """Obtém uma interação existente ou cria uma nova."""
        if session_id in self._active_interactions:
            return self._active_interactions[session_id]
        
        interaction = Interaction(session_id=session_id, user_id=user_id)
        self._active_interactions[session_id] = interaction
        return interaction
    
    async def _update_session_context(self, session: Session, message: Message) -> None:
        """Atualiza o contexto da sessão com base na mensagem recebida."""
        # Atualiza o último intent detectado
        session.context.last_intent = message.intent
        
        # Atualiza a tendência de sentimento (média móvel)
        if message.sentiment_score is not None:
            alpha = 0.3  # Fator de suavização para a média móvel
            session.context.sentiment_trend = (alpha * message.sentiment_score + 
                                            (1 - alpha) * session.context.sentiment_trend)
        
        # Extrai e atualiza informações específicas baseadas em entidades detectadas
        for entity in message.entities:
            if entity.type == "product":
                product_id = entity.value
                session.add_viewed_product(product_id)
            elif entity.type == "category":
                session.context.last_category = entity.value
            elif entity.type == "search_query":
                session.context.search_query = entity.value
        
        # Atualiza o estágio da conversa com base na intenção
        if message.intent == "greeting":
            session.set_stage(ConversationStage.GREETING)
        elif message.intent in ["search_product", "browse_category", "list_products"]:
            session.set_stage(ConversationStage.EXPLORING)
        elif message.intent in ["product_info", "product_details"]:
            session.set_stage(ConversationStage.PRODUCT_DETAILS)
        elif message.intent in ["add_to_cart", "view_cart", "remove_from_cart"]:
            session.set_stage(ConversationStage.CART_MANAGEMENT)
        elif message.intent in ["checkout", "payment"]:
            session.set_stage(ConversationStage.CHECKOUT)
        elif message.intent == "support":
            session.set_stage(ConversationStage.SUPPORT)
        
        # Em uma implementação real, salvaríamos as alterações no banco de dados
        await self.session_service.update_session_context(
            session.id,
            {
                "last_intent": session.context.last_intent,
                "current_stage": session.context.current_stage,
                "products_viewed": session.context.products_viewed,
                "last_product_id": session.context.last_product_id,
                "last_category": session.context.last_category,
                "search_query": session.context.search_query,
                "sentiment_trend": session.context.sentiment_trend
            }
        )
    
    async def _generate_response(self, user: User, session: Session, message: Message, 
                               persuasion_technique: Optional[str]) -> str:
        """Gera uma resposta com base na intenção detectada e no contexto da sessão."""
        # Em uma implementação real, usaríamos um LLM mais complexo aqui
        intent = message.intent or "unknown"
        stage = session.context.current_stage
        
        # Constrói o contexto para geração da resposta
        context = {
            "user_name": user.name or "cliente",
            "is_returning_customer": user.is_returning_customer(),
            "user_tier": user.tier.value,
            "session_stage": stage,
            "last_product_id": session.context.last_product_id,
            "last_category": session.context.last_category,
            "search_query": session.context.search_query,
            "products_viewed": session.context.products_viewed,
            "sentiment_trend": session.context.sentiment_trend,
        }
        
        # Adiciona informações do carrinho, se disponível
        if session.context.cart_id:
            cart = await self.cart_service.get_cart(session.context.cart_id)
            if cart:
                context["cart_item_count"] = cart.get_item_count()
                context["cart_total"] = cart.totals.grand_total
        
        # Cria uma resposta baseada na intent e contexto
        return await self.nlp_service.generate_response(intent, message.entities, context)
    
    async def _send_response(self, user: User, session: Session, response_text: str, 
                           persuasion_technique: Optional[str]) -> None:
        """Envia a resposta ao usuário via WhatsApp."""
        # Cria um ID para a mensagem de resposta
        message_id = str(uuid.uuid4())
        
        # Prepara o conteúdo da mensagem
        content = MessageContent(text=response_text)
        
        # Cria o objeto Message para a resposta
        response_message = Message(
            id=message_id,
            session_id=session.id,
            user_id=user.id,
            timestamp=datetime.now(),
            direction=MessageDirection.OUTGOING,
            type=MessageType.TEXT,
            content=content,
            techniques_used=[persuasion_technique] if persuasion_technique else []
        )
        
        # Adiciona a mensagem à interação atual
        interaction = self._active_interactions.get(session.id)
        if interaction:
            interaction.add_message(response_message)
        
        # Envia a mensagem via WhatsApp
        await self.whatsapp_service.send_text_message(user.phone, response_text)
        
        # Em um sistema real, salvaríamos a mensagem no banco de dados
    
    async def send_product_recommendations(self, user_id: str, session_id: str, 
                                         product_ids: List[str], intro_text: str) -> None:
        """Envia recomendações de produtos para o usuário."""
        try:
            # Obtém o usuário
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                logger.error(f"User not found: {user_id}")
                return
            
            # Obtém os produtos
            products = []
            for product_id in product_ids:
                product = await self.catalog_service.get_product_by_id(product_id)
                if product:
                    products.append(product)
            
            if not products:
                logger.warning(f"No valid products found in IDs: {product_ids}")
                return
            
            # Envia os produtos via WhatsApp
            await self.whatsapp_service.send_product_message(user.phone, products, intro_text)
            
            # Cria mensagem para registro
            message_id = str(uuid.uuid4())
            content = MessageContent(
                text=intro_text,
                product_ids=product_ids
            )
            
            # Cria o objeto Message para a resposta
            message = Message(
                id=message_id,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                direction=MessageDirection.OUTGOING,
                type=MessageType.PRODUCT,
                content=content
            )
            
            # Adiciona a mensagem à interação atual
            interaction = self._active_interactions.get(session_id)
            if interaction:
                interaction.add_message(message)
            
            # Registra a recomendação nas métricas
            await self.metrics_service.track_interaction(
                user_id=user_id,
                session_id=session_id,
                interaction_type="product_recommendation",
                metadata={
                    "product_ids": product_ids,
                    "products_count": len(products)
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending product recommendations: {e}", exc_info=True)
    
    async def manage_cart(self, user_id: str, session_id: str, action: str, 
                        product_id: str, quantity: int = 1, variant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Gerencia operações de carrinho como adicionar ou remover itens.
        Retorna um dicionário com o resultado da operação.
        """
        try:
            # Obtém a sessão
            session = await self.session_service.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Obtém ou cria um carrinho para a sessão
            cart_id = session.context.cart_id
            
            if not cart_id:
                # Cria um novo carrinho
                cart = await self.cart_service.create_cart(user_id, session_id)
                cart_id = cart.id
                
                # Atualiza o contexto da sessão com o ID do carrinho
                session.context.cart_id = cart_id
                await self.session_service.update_session_context(
                    session_id, {"cart_id": cart_id}
                )
            else:
                # Obtém o carrinho existente
                cart = await self.cart_service.get_cart(cart_id)
                if not cart:
                    return {"success": False, "error": "Cart not found"}
            
            # Executa a ação solicitada
            result = {"success": True, "action": action}
            
            if action == "add":
                success, item = await self.cart_service.add_item_to_cart(
                    cart_id, product_id, quantity, variant_id
                )
                result["success"] = success
                if success and item:
                    result["item"] = {
                        "product_id": item.product_id,
                        "name": item.name,
                        "quantity": item.quantity,
                        "total_price": item.total_price
                    }
                    
                    # Registra a conversão nas métricas
                    await self.metrics_service.track_conversion(
                        user_id=user_id,
                        session_id=session_id,
                        conversion_type="add_to_cart",
                        value=item.total_price,
                        metadata={
                            "product_id": product_id,
                            "quantity": quantity,
                            "variant_id": variant_id
                        }
                    )
            
            elif action == "remove":
                success = await self.cart_service.remove_item_from_cart(
                    cart_id, product_id, variant_id
                )
                result["success"] = success
            
            elif action == "update":
                success = await self.cart_service.update_item_quantity(
                    cart_id, product_id, quantity, variant_id
                )
                result["success"] = success
            
            elif action == "clear":
                success = await self.cart_service.clear_cart(cart_id)
                result["success"] = success
            
            else:
                result["success"] = False
                result["error"] = f"Unknown action: {action}"
            
            # Obtém o carrinho atualizado
            updated_cart = await self.cart_service.get_cart(cart_id)
            if updated_cart:
                result["cart"] = {
                    "item_count": updated_cart.get_item_count(),
                    "total": updated_cart.totals.grand_total
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error managing cart: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def generate_checkout(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Gera um link de checkout para o carrinho atual."""
        try:
            # Obtém a sessão
            session = await self.session_service.get_session(session_id)
            if not session or not session.context.cart_id:
                return {"success": False, "error": "No active cart found"}
            
            # Gera o link de checkout
            checkout_url = await self.cart_service.generate_checkout_url(session.context.cart_id)
            
            if not checkout_url:
                return {"success": False, "error": "Failed to generate checkout URL"}
            
            # Atualiza o estágio da sessão
            session.set_stage(ConversationStage.CHECKOUT)
            await self.session_service.update_session_context(
                session_id, {"current_stage": ConversationStage.CHECKOUT}
            )
            
            # Obtém o usuário
            user = await self.user_service.get_user_by_id(user_id)
            
            # Envia uma mensagem com o link de checkout
            message = (
                f"Ótimo! Seu carrinho está pronto para checkout. "
                f"Clique no link abaixo para finalizar sua compra:\n\n"
                f"{checkout_url}"
            )
            
            await self.whatsapp_service.send_text_message(user.phone, message)
            
            # Registra a conversão
            cart = await self.cart_service.get_cart(session.context.cart_id)
            if cart:
                await self.metrics_service.track_conversion(
                    user_id=user_id,
                    session_id=session_id,
                    conversion_type="checkout_initiated",
                    value=cart.totals.grand_total,
                    metadata={
                        "cart_id": session.context.cart_id,
                        "item_count": cart.get_item_count()
                    }
                )
            
            return {
                "success": True, 
                "checkout_url": checkout_url
            }
            
        except Exception as e:
            logger.error(f"Error generating checkout: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def close_session(self, session_id: str) -> bool:
        """Fecha uma sessão e limpa os recursos associados."""
        try:
            # Remove do cache
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
            
            if session_id in self._active_interactions:
                del self._active_interactions[session_id]
            
            # Marca como fechada no banco de dados
            success = await self.session_service.close_session(session_id)
            
            return success
        except Exception as e:
            logger.error(f"Error closing session: {e}", exc_info=True)
            return False
    
    async def handle_scheduled_tasks(self) -> None:
        """
        Executa tarefas agendadas como limpeza de sessões expiradas 
        e envio de lembretes de carrinho abandonado.
        """
        try:
            # Limpa sessões expiradas
            cleaned_count = await self.session_service.clean_expired_sessions()
            if cleaned_count > 0:
                logger.info(f"Cleaned {cleaned_count} expired sessions")
            
            # Aqui poderia implementar outras tarefas programadas como:
            # - Enviar lembretes de carrinho abandonado
            # - Recomendar produtos para usuários inativos
            # - Atualizar métricas e relatórios
            
        except Exception as e:
            logger.error(f"Error in scheduled tasks: {e}", exc_info=True)

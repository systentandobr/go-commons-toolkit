import json
import aiohttp
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

from app.models.product import Product
from app.models.interaction import Message, MessageContent, MessageDirection, MessageType
from app.services.interfaces import WhatsAppServiceInterface
from app.utils.config import settings

logger = logging.getLogger(__name__)

class WhatsAppService(WhatsAppServiceInterface):
    """Implementação do serviço de integração com a API do WhatsApp Business."""
    
    def __init__(self):
        self.base_url = settings.WHATSAPP_API_URL
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.version = settings.WHATSAPP_API_VERSION
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        
    async def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Faz uma requisição para a API do WhatsApp."""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{self.version}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await response.json()
                elif method.upper() == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json()
                elif method.upper() == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        return await response.json()
                elif method.upper() == "PUT":
                    async with session.put(url, headers=headers, json=data) as response:
                        return await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
        except Exception as e:
            logger.error(f"Error making WhatsApp API request: {e}")
            raise
    
    async def send_text_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Envia uma mensagem de texto para o número especificado."""
        endpoint = f"{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        response = await self._make_api_request("POST", endpoint, data)
        logger.info(f"Sent text message to {phone_number}. Response: {response}")
        return response
    
    async def send_image_message(self, phone_number: str, image_url: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Envia uma mensagem de imagem para o número especificado."""
        endpoint = f"{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "image",
            "image": {
                "link": image_url
            }
        }
        
        if caption:
            data["image"]["caption"] = caption
        
        response = await self._make_api_request("POST", endpoint, data)
        logger.info(f"Sent image message to {phone_number}. Response: {response}")
        return response
    
    async def send_product_message(self, phone_number: str, products: List[Product], caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia uma mensagem com múltiplos produtos usando um template de carrossel.
        Como a API não suporta diretamente envio de múltiplos produtos, adaptamos para enviar uma mensagem
        com imagens e texto ou um template de carrossel.
        """
        if not products:
            logger.warning("No products provided to send_product_message")
            return {"error": "No products provided"}
        
        if len(products) == 1:
            # Se apenas um produto, enviamos uma imagem com caption
            product = products[0]
            image_url = product.get_main_image_url()
            if not image_url:
                return await self.send_text_message(phone_number, 
                                                   f"*{product.name}*\n{product.description}\n\nPreço: {product.get_display_price()}")
            
            product_caption = caption or f"*{product.name}*\n{product.description}\n\nPreço: {product.get_display_price()}"
            return await self.send_image_message(phone_number, image_url, product_caption)
        
        # Se múltiplos produtos, enviamos um template de carrossel ou múltiplas mensagens
        if settings.WHATSAPP_SUPPORTS_CAROUSEL:
            # Implementação de template de carrossel se suportado
            return await self._send_carousel_template(phone_number, products, caption)
        
        # Fallback para múltiplas mensagens de imagem
        intro_message = caption or f"Encontrei {len(products)} produtos que podem te interessar:"
        await self.send_text_message(phone_number, intro_message)
        
        responses = []
        for product in products:
            response = await self.send_image_message(
                phone_number, 
                product.get_main_image_url() or settings.DEFAULT_PRODUCT_IMAGE,
                f"*{product.name}*\n{product.description[:100]}...\n\nPreço: {product.get_display_price()}"
            )
            responses.append(response)
        
        return {"multiple_responses": responses}
    
    async def _send_carousel_template(self, phone_number: str, products: List[Product], caption: Optional[str] = None) -> Dict[str, Any]:
        """Envia um template de carrossel com múltiplos produtos."""
        endpoint = f"{self.phone_number_id}/messages"
        
        components = []
        if caption:
            components.append({
                "type": "header",
                "parameters": [
                    {
                        "type": "text",
                        "text": caption
                    }
                ]
            })
        
        # Adiciona os produtos ao carrossel
        carousel_items = []
        for product in products[:10]:  # Limite de 10 itens no carrossel
            carousel_items.append({
                "title": product.name,
                "subtitle": product.description[:80] + "..." if len(product.description) > 80 else product.description,
                "image_url": product.get_main_image_url() or settings.DEFAULT_PRODUCT_IMAGE,
                "price": product.get_display_price()
            })
        
        components.append({
            "type": "carousel",
            "parameters": carousel_items
        })
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": "product_carousel",
                "language": {
                    "code": "pt_BR"
                },
                "components": components
            }
        }
        
        response = await self._make_api_request("POST", endpoint, data)
        logger.info(f"Sent carousel template to {phone_number}. Response: {response}")
        return response
    
    async def send_quick_reply_message(self, phone_number: str, message: str, options: List[str]) -> Dict[str, Any]:
        """Envia uma mensagem com opções de resposta rápida."""
        endpoint = f"{self.phone_number_id}/messages"
        
        # Limita a 3 opções para evitar problemas com a API
        buttons = []
        for option in options[:3]:
            buttons.append({
                "type": "reply",
                "reply": {
                    "id": f"option_{len(buttons)}",
                    "title": option
                }
            })
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": message
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        response = await self._make_api_request("POST", endpoint, data)
        logger.info(f"Sent quick reply message to {phone_number}. Response: {response}")
        return response
    
    async def send_template_message(self, phone_number: str, template_name: str, template_params: Dict[str, Any]) -> Dict[str, Any]:
        """Envia uma mensagem usando um template pré-aprovado."""
        endpoint = f"{self.phone_number_id}/messages"
        
        # Converte os parâmetros para o formato esperado pela API
        components = []
        if "header_params" in template_params:
            header_parameters = []
            for param in template_params["header_params"]:
                header_parameters.append({
                    "type": param["type"],
                    "text": param["text"] if param["type"] == "text" else None,
                    "image": {"link": param["url"]} if param["type"] == "image" else None,
                    "document": {"link": param["url"]} if param["type"] == "document" else None,
                    "video": {"link": param["url"]} if param["type"] == "video" else None
                })
            
            components.append({
                "type": "header",
                "parameters": header_parameters
            })
        
        if "body_params" in template_params:
            body_parameters = []
            for param in template_params["body_params"]:
                body_parameters.append({
                    "type": "text",
                    "text": param
                })
            
            components.append({
                "type": "body",
                "parameters": body_parameters
            })
        
        if "button_params" in template_params:
            button_parameters = []
            for param in template_params["button_params"]:
                button_parameters.append({
                    "type": "text",
                    "text": param
                })
            
            components.append({
                "type": "button",
                "sub_type": "quick_reply",
                "index": "0",
                "parameters": button_parameters
            })
        
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": template_params.get("language_code", "pt_BR")
                },
                "components": components
            }
        }
        
        response = await self._make_api_request("POST", endpoint, data)
        logger.info(f"Sent template message to {phone_number}. Response: {response}")
        return response
    
    async def process_incoming_message(self, webhook_data: Dict[str, Any]) -> Message:
        """Processa uma mensagem recebida via webhook e retorna um objeto Message."""
        try:
            entry = webhook_data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            message_obj = value.get("messages", [])[0]
            
            message_id = message_obj.get("id")
            from_number = message_obj.get("from")
            timestamp = datetime.fromtimestamp(int(message_obj.get("timestamp")))
            
            # Extrair o tipo e conteúdo da mensagem
            message_type = message_obj.get("type")
            content = MessageContent()
            
            if message_type == "text":
                content.text = message_obj.get("text", {}).get("body")
                msg_type = MessageType.TEXT
            elif message_type == "image":
                content.media_url = message_obj.get("image", {}).get("url")
                content.text = message_obj.get("image", {}).get("caption")
                msg_type = MessageType.IMAGE
            elif message_type == "interactive":
                interactive_data = message_obj.get("interactive", {})
                interactive_type = interactive_data.get("type")
                
                if interactive_type == "button_reply":
                    content.text = interactive_data.get("button_reply", {}).get("title")
                    content.metadata = {"button_id": interactive_data.get("button_reply", {}).get("id")}
                elif interactive_type == "list_reply":
                    content.text = interactive_data.get("list_reply", {}).get("title")
                    content.metadata = {"list_id": interactive_data.get("list_reply", {}).get("id")}
                
                msg_type = MessageType.QUICK_REPLY
            else:
                content.text = f"Mensagem do tipo {message_type} não suportada ainda."
                msg_type = MessageType.TEXT
            
            # Cria e retorna o objeto Message
            message = Message(
                id=message_id,
                session_id="temp_session_id",  # Será atualizado pelo agente
                user_id="temp_user_id",  # Será atualizado pelo agente
                timestamp=timestamp,
                direction=MessageDirection.INCOMING,
                type=msg_type,
                content=content,
                metadata={
                    "phone_number": from_number,
                    "raw_data": message_obj
                }
            )
            
            logger.info(f"Processed incoming message: {message_id} from {from_number}")
            return message
            
        except Exception as e:
            logger.error(f"Error processing webhook data: {e}")
            logger.debug(f"Webhook data: {json.dumps(webhook_data)}")
            
            # Retorna uma mensagem de erro em caso de falha
            return Message(
                id=str(uuid.uuid4()),
                session_id="error_session",
                user_id="error_user",
                timestamp=datetime.now(),
                direction=MessageDirection.INCOMING,
                type=MessageType.TEXT,
                content=MessageContent(text="[Erro ao processar mensagem]"),
                metadata={"error": str(e), "webhook_data": webhook_data}
            )
    
    async def mark_message_as_read(self, message_id: str) -> bool:
        """Marca uma mensagem como lida no WhatsApp."""
        endpoint = f"{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = await self._make_api_request("POST", endpoint, data)
            return "success" in response and response["success"]
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False
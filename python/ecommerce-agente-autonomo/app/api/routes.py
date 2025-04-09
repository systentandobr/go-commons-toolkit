from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Body
from typing import Dict, Any, List
import logging

from app.core.agent import AutonomousAgent
from app.utils.logger import logger
from app.utils.config import settings

# Router principal para API
router = APIRouter()

# Dependência para obter o agente
def get_agent():
    # Em uma aplicação real, isso seria injetado via DI ou outra forma
    from app.core.dependencies import get_autonomous_agent
    return get_autonomous_agent()

@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks, agent: AutonomousAgent = Depends(get_agent)):
    """
    Endpoint para receber webhooks do WhatsApp.
    Processa a mensagem de forma assíncrona em uma tarefa de fundo.
    """
    try:
        # Parse do corpo da requisição
        webhook_data = await request.json()
        logger.debug(f"Received webhook: {webhook_data}")
        
        # Verifica se é uma verificação de webhook
        if webhook_data.get("object") == "whatsapp_business_account":
            # Verifica se há mensagens no webhook
            if "entry" in webhook_data and webhook_data["entry"]:
                entry = webhook_data["entry"][0]
                if "changes" in entry and entry["changes"]:
                    change = entry["changes"][0]
                    if "value" in change and "messages" in change["value"]:
                        # Processa a mensagem de forma assíncrona
                        background_tasks.add_task(agent.process_webhook, webhook_data)
                        return {"status": "processing"}
        
        # Se não for uma mensagem válida
        return {"status": "ignored"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Endpoint para verificação do webhook pelo WhatsApp.
    """
    try:
        # Obtém os parâmetros de query
        params = dict(request.query_params)
        
        # Verifica o modo e token
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        
        if mode == "subscribe" and token == settings.WHATSAPP_WEBHOOK_TOKEN:
            logger.info("Webhook verification successful")
            # Retorna o desafio para confirmar a verificação
            return int(challenge) if challenge else "Verified"
        
        logger.warning(f"Webhook verification failed: {params}")
        raise HTTPException(status_code=403, detail="Verification failed")
        
    except Exception as e:
        logger.error(f"Error verifying webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/send-product-recommendations")
async def send_recommendations(
    data: Dict[str, Any] = Body(...),
    agent: AutonomousAgent = Depends(get_agent)
):
    """
    Endpoint para enviar recomendações de produtos para um usuário.
    """
    try:
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        product_ids = data.get("product_ids", [])
        intro_text = data.get("intro_text", "Olha só estas recomendações para você:")
        
        if not user_id or not session_id or not product_ids:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Envia as recomendações de forma assíncrona
        await agent.send_product_recommendations(user_id, session_id, product_ids, intro_text)
        
        return {"status": "success", "message": "Recommendations sent"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cart/{action}")
async def manage_cart(
    action: str,
    data: Dict[str, Any] = Body(...),
    agent: AutonomousAgent = Depends(get_agent)
):
    """
    Endpoint para gerenciar o carrinho de compras.
    Ações: add, remove, update, clear
    """
    try:
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)
        variant_id = data.get("variant_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        if action not in ["add", "remove", "update", "clear"] and not product_id and action != "clear":
            raise HTTPException(status_code=400, detail="Invalid action or missing product_id")
        
        # Executa a ação do carrinho
        result = await agent.manage_cart(user_id, session_id, action, product_id, quantity, variant_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Cart operation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cart operation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/checkout")
async def generate_checkout(
    data: Dict[str, Any] = Body(...),
    agent: AutonomousAgent = Depends(get_agent)
):
    """
    Endpoint para gerar um checkout para o carrinho atual.
    """
    try:
        user_id = data.get("user_id")
        session_id = data.get("session_id")
        
        if not user_id or not session_id:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Gera o checkout
        result = await agent.generate_checkout(user_id, session_id)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Checkout generation failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating checkout: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    agent: AutonomousAgent = Depends(get_agent)
):
    """
    Endpoint para fechar uma sessão.
    """
    try:
        # Fecha a sessão
        success = await agent.close_session(session_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to close session")
        
        return {"status": "success", "message": "Session closed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """
    Endpoint para verificação de saúde da API.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "name": settings.APP_NAME
    }

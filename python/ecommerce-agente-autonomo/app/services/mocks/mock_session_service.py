import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.session import Session, SessionContext
from app.services.interfaces import SessionServiceInterface
from app.utils.logger import logger

class MockSessionService(SessionServiceInterface):
    """Serviço mock para gerenciamento de sessões."""
    
    def __init__(self):
        """Inicializa o serviço com um dicionário de sessões em memória."""
        self.sessions = {}
        
    async def create_session(self, user_id: str, channel: str) -> Session:
        """Cria uma nova sessão para o usuário."""
        # Cria um novo ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Cria a nova sessão
        session = Session(
            id=session_id,
            user_id=user_id,
            channel=channel,
            started_at=datetime.now(),
            last_activity_at=datetime.now(),
            context=SessionContext(),
            is_active=True
        )
        
        # Adiciona ao dicionário
        self.sessions[session.id] = session
        
        logger.info(f"Created new session: {session.id} for user: {user_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Obtém uma sessão pelo ID."""
        return self.sessions.get(session_id)
    
    async def get_active_session_by_user(self, user_id: str, channel: str) -> Optional[Session]:
        """Obtém a sessão ativa do usuário em um determinado canal."""
        # Encontra a sessão ativa mais recente
        active_sessions = [
            session for session in self.sessions.values()
            if session.user_id == user_id and session.channel == channel and session.is_active and not session.is_expired()
        ]
        
        if not active_sessions:
            return None
        
        # Retorna a sessão mais recente
        return max(active_sessions, key=lambda s: s.last_activity_at)
    
    async def update_session_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """Atualiza o contexto de uma sessão."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Atualiza os campos do contexto
        for key, value in context_updates.items():
            if hasattr(session.context, key):
                setattr(session.context, key, value)
        
        # Atualiza a última atividade
        session.last_activity_at = datetime.now()
        
        logger.info(f"Updated context for session: {session.id}")
        return True
    
    async def close_session(self, session_id: str) -> bool:
        """Fecha uma sessão."""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Marca como inativa
        session.is_active = False
        
        logger.info(f"Closed session: {session.id}")
        return True
    
    async def clean_expired_sessions(self, timeout_minutes: int = 30) -> int:
        """Limpa sessões expiradas e retorna o número de sessões limpas."""
        expired_count = 0
        
        for session_id, session in list(self.sessions.items()):
            if session.is_expired(timeout_minutes):
                # Marca como inativa
                session.is_active = False
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned {expired_count} expired sessions")
        
        return expired_count

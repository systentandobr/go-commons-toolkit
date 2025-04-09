from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ExporterBase(ABC):
    """Classe base para exportadores de resultados."""
    
    @abstractmethod
    def export(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Exporta os resultados da análise para um formato específico.
        
        Args:
            data: Dados a serem exportados
            output_path: Caminho onde salvar o arquivo
            
        Returns:
            Caminho para o arquivo exportado
        """
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """
        Retorna o nome do formato de exportação.
        
        Returns:
            Nome do formato
        """
        pass
    
    @property
    @abstractmethod
    def mime_type(self) -> str:
        """
        Retorna o MIME type do formato de exportação.
        
        Returns:
            MIME type
        """
        pass

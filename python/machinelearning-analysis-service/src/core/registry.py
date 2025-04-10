from typing import Dict, List, Any, Optional, Type
from .protocols import ModelProtocol, ExecutionContextProtocol
from ..models.base import ModelContext
from ..exporters.exporter_base import ExporterBase

class ModelRegistry:
    """Registro global de modelos disponíveis."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._models = {}
            cls._instance._contexts = {}
        return cls._instance
    
    def register_model(self, model: ModelProtocol) -> None:
        """Registra um modelo no registro."""
        model_key = f"{model.model_id}@{model.version}"
        self._models[model_key] = model
    
    def register_context(self, name: str, context: ExecutionContextProtocol) -> None:
        """Registra um contexto de execução no registro."""
        self._contexts[name] = context
    
    def get_model(self, model_id: str, version: str = "latest") -> Optional[ModelProtocol]:
        """Obtém um modelo pelo ID e versão."""
        # Se for "latest", encontrar a versão mais recente
        if version == "latest":
            latest_version = self._find_latest_version(model_id)
            if latest_version:
                model_key = f"{model_id}@{latest_version}"
                return self._models.get(model_key)
            return None
        
        # Versão específica
        model_key = f"{model_id}@{version}"
        return self._models.get(model_key)
    
    def _find_latest_version(self, model_id: str) -> Optional[str]:
        """Encontra a versão mais recente de um modelo pelo ID."""
        versions = []
        prefix = f"{model_id}@"
        
        # Coletar todas as versões do modelo
        for key in self._models.keys():
            if key.startswith(prefix):
                version = key[len(prefix):]
                versions.append(version)
        
        if not versions:
            return None
        
        # Ordena as versões (assumindo formato semântico x.y.z)
        # Pode ser necessário uma lógica mais sofisticada dependendo do formato de versão
        try:
            sorted_versions = sorted(versions, key=lambda v: [int(x) for x in v.split('.')])
            return sorted_versions[-1]  # Última versão
        except:
            # Fallback para ordenação alfabética se o formato não for numérico
            return sorted(versions)[-1]
    
    def get_context(self, name: str) -> Optional[ExecutionContextProtocol]:
        """Obtém um contexto de execução pelo nome."""
        return self._contexts.get(name)
    
    def create_model_context(
        self, model_id: str, version: str = "latest", context_name: str = "default"
    ) -> Optional[ModelContext]:
        """Cria um ModelContext combinando um modelo e um contexto."""
        model = self.get_model(model_id, version)
        context = self.get_context(context_name)
        
        if model is None or context is None:
            return None
        
        return ModelContext(model, context)
    
    def list_available_models(self) -> List[Dict[str, str]]:
        """Lista todos os modelos disponíveis no registro."""
        models = []
        for model_key in self._models:
            model_id, version = model_key.split('@')
            models.append({"id": model_id, "version": version})
        return models
    
    def list_available_contexts(self) -> List[str]:
        """Lista todos os contextos disponíveis no registro."""
        return list(self._contexts.keys())
    
    def get_model_metadata(self, model_id: str, version: str = "latest") -> Optional[Dict[str, Any]]:
        """Obtém metadados de um modelo específico."""
        model = self.get_model(model_id, version)
        if model is None:
            return None
        
        # Extrair metadados básicos do modelo
        metadata = {
            "id": model.model_id,
            "version": model.version
        }
        
        # Adicionar metadados específicos se disponíveis
        if hasattr(model, 'metadata'):
            metadata.update(model.metadata)
        
        return metadata


class ExporterRegistry:
    """Registro global de exportadores disponíveis."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExporterRegistry, cls).__new__(cls)
            cls._instance._exporters = {}
        return cls._instance
    
    def register_exporter(self, format_name: str, exporter_class: Type[ExporterBase]) -> None:
        """Registra um exportador no sistema."""
        self._exporters[format_name.lower()] = exporter_class
    
    def get_exporter(self, format_name: str) -> Optional[ExporterBase]:
        """Obtém um exportador pelo nome do formato."""
        exporter_class = self._exporters.get(format_name.lower())
        if exporter_class:
            return exporter_class()
        return None
    
    def list_supported_formats(self) -> Dict[str, str]:
        """Lista formatos de exportação suportados."""
        return {
            format_name: exporter_class().mime_type
            for format_name, exporter_class in self._exporters.items()
        }

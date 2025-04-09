from typing import Dict, Any
import json
import numpy as np
from .exporter_base import ExporterBase

class JsonExporter(ExporterBase):
    """Exportador para formato JSON."""
    
    @property
    def format_name(self) -> str:
        return "json"
    
    @property
    def mime_type(self) -> str:
        return "application/json"
    
    def export(self, data: Dict[str, Any], output_path: str) -> str:
        """Exporta resultados para JSON."""
        # Converter arrays numpy e outros tipos não serializáveis
        serializable_data = self._convert_numpy(data)
        
        # Salvar no arquivo especificado
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _convert_numpy(self, obj: Any) -> Any:
        """Converte arrays numpy e outros tipos não serializáveis para JSON."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list) or isinstance(obj, tuple):
            return [self._convert_numpy(i) for i in obj]
        else:
            return obj

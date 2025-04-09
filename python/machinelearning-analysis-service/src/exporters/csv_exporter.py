from typing import Dict, Any, List
import pandas as pd
import numpy as np
from .exporter_base import ExporterBase

class CsvExporter(ExporterBase):
    """Exportador para formato CSV."""
    
    @property
    def format_name(self) -> str:
        return "csv"
    
    @property
    def mime_type(self) -> str:
        return "text/csv"
    
    def export(self, data: Dict[str, Any], output_path: str) -> str:
        """Exporta resultados para CSV."""
        # Converter para DataFrame do pandas
        df = self._convert_to_dataframe(data)
        
        # Salvar como CSV
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        return output_path
    
    def _convert_to_dataframe(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Converte dados hierárquicos para formato DataFrame."""
        # Verificar se temos tipos de dados específicos
        if "detections" in data:
            # Resultados de detecção de objetos
            return pd.DataFrame(data["detections"])
        
        elif "predictions" in data:
            # Resultados de classificação
            return pd.DataFrame(data["predictions"])
        
        elif "frames" in data and isinstance(data["frames"], list):
            # Resultados de vídeo
            frames_data = []
            for i, frame in enumerate(data["frames"]):
                if "detections" in frame:
                    frame_df = pd.DataFrame(frame["detections"])
                    frame_df["frame_id"] = i
                    frames_data.append(frame_df)
                elif "predictions" in frame:
                    frame_df = pd.DataFrame(frame["predictions"])
                    frame_df["frame_id"] = i
                    frames_data.append(frame_df)
            
            if frames_data:
                return pd.concat(frames_data, ignore_index=True)
        
        # Se nenhum dos formatos específicos for encontrado,
        # tentar normalizar estrutura genérica
        try:
            # Usar pandas para normalizar JSON aninhado
            return pd.json_normalize(data)
        except:
            # Fallback: extrair apenas metadados ou criar DataFrame vazio
            meta_data = {}
            if "metadata" in data:
                meta_data = self._flatten_dict(data["metadata"])
            
            if meta_data:
                return pd.DataFrame([meta_data])
            else:
                return pd.DataFrame()
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """Achata um dicionário aninhado para um formato de linha única."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            elif isinstance(v, (list, tuple)) and len(v) > 0 and not isinstance(v[0], dict):
                # Converter listas simples para string
                items.append((new_key, str(v)))
            elif isinstance(v, (list, tuple)) and len(v) > 0 and isinstance(v[0], dict):
                # Ignorar listas de dicionários (muito complexas para CSV de linha única)
                items.append((new_key, f"[{len(v)} items]"))
            else:
                items.append((new_key, v))
        
        return dict(items)

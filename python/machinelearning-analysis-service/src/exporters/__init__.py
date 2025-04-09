from typing import Dict, Optional, Type
from .exporter_base import ExporterBase
from .json_exporter import JsonExporter
from .csv_exporter import CsvExporter

# Registro de exportadores disponíveis
EXPORTERS: Dict[str, Type[ExporterBase]] = {
    "json": JsonExporter,
    "csv": CsvExporter,
}

def get_exporter(format_name: str) -> Optional[ExporterBase]:
    """
    Obtém uma instância de exportador pelo nome do formato.
    
    Args:
        format_name: Nome do formato (json, csv, etc.)
        
    Returns:
        Instância do exportador ou None se o formato não for suportado
    """
    exporter_class = EXPORTERS.get(format_name.lower())
    if exporter_class:
        return exporter_class()
    return None

def list_supported_formats() -> Dict[str, str]:
    """
    Lista formatos de exportação suportados.
    
    Returns:
        Dicionário com nomes de formatos e seus MIME types
    """
    return {
        format_name: exporter_class().mime_type
        for format_name, exporter_class in EXPORTERS.items()
    }

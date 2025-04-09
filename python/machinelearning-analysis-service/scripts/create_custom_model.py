#!/usr/bin/env python3
"""
Script para criar e registrar modelos personalizados.

Este script demonstra como criar um modelo personalizado e registrá-lo
no serviço de análise.
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path

# Configurar paths para importar módulos do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core.registry import ModelRegistry
from src.models.generic.generic_model import GenericModel

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def create_custom_model(config_file, register=True):
    """
    Cria um modelo personalizado a partir de um arquivo de configuração.
    
    Args:
        config_file: Caminho para arquivo JSON de configuração
        register: Se True, registra o modelo no Registry
        
    Returns:
        Instância do modelo criado
    """
    logger.info(f"Criando modelo personalizado a partir de {config_file}")
    
    # Carregar configuração
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Validar configuração mínima
    required_fields = ['model_id', 'version', 'model_path', 'task_type', 'input_shape']
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        logger.error(f"Configuração inválida. Campos faltando: {', '.join(missing_fields)}")
        return None
    
    # Criar modelo genérico
    try:
        model = GenericModel(
            model_id=config['model_id'],
            version=config['version'],
            model_path=config['model_path'],
            task_type=config['task_type'],
            input_shape=config['input_shape'],
            preprocessing_config=config.get('preprocessing_config', {}),
            postprocessing_config=config.get('postprocessing_config', {}),
            metadata=config.get('metadata', {})
        )
        
        logger.info(f"Modelo {model.model_id}@{model.version} criado com sucesso")
        
        # Registrar modelo se solicitado
        if register:
            registry = ModelRegistry()
            registry.register_model(model)
            logger.info(f"Modelo {model.model_id}@{model.version} registrado com sucesso")
        
        return model
        
    except Exception as e:
        logger.error(f"Erro ao criar modelo: {e}")
        return None


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Criar modelo personalizado")
    parser.add_argument("--config", type=str, required=True,
                        help="Caminho para arquivo de configuração JSON")
    parser.add_argument("--no-register", action="store_true",
                        help="Não registrar o modelo no Registry")
    
    args = parser.parse_args()
    
    # Criar modelo
    model = create_custom_model(args.config, not args.no_register)
    
    if model:
        logger.info("Modelo criado com sucesso")
        sys.exit(0)
    else:
        logger.error("Falha ao criar modelo")
        sys.exit(1)


if __name__ == "__main__":
    main()

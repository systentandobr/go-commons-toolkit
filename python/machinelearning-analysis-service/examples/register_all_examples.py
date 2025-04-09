#!/usr/bin/env python3
"""
Script para registrar todos os modelos de exemplo.

Este script percorre os módulos de exemplo e registra todos os modelos
disponíveis no ModelRegistry.
"""

import os
import sys
import importlib
import logging

# Configurar path para incluir a raiz do projeto
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def register_food_analysis_models():
    """Registra modelos do exemplo de análise nutricional."""
    try:
        from examples.food_analysis.food_nutrition_model import register_food_nutrition_model
        model = register_food_nutrition_model()
        logger.info(f"Modelo {model.model_id}@{model.version} registrado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao registrar modelos de análise nutricional: {e}")
        return False


def main():
    """Função principal."""
    logger.info("Registrando modelos de exemplo...")
    
    # Registrar modelos de cada exemplo
    success = True
    
    # Análise nutricional
    if not register_food_analysis_models():
        success = False
    
    # ... outros exemplos seriam adicionados aqui
    
    # Relatório final
    if success:
        logger.info("Todos os modelos de exemplo foram registrados com sucesso!")
        return 0
    else:
        logger.warning("Houve erros ao registrar alguns modelos")
        return 1


if __name__ == "__main__":
    sys.exit(main())

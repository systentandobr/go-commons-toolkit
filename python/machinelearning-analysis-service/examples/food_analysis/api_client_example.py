#!/usr/bin/env python3
"""
Exemplo de cliente para a API de análise nutricional.

Este script demonstra como utilizar a API para analisar imagens de alimentos
e obter informações nutricionais.
"""

import os
import sys
import argparse
import json
import requests
from pprint import pprint
from urllib.parse import urljoin

# Configurar path para incluir a raiz do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


def analyze_food_image(image_path, api_url="http://localhost:8000/api", model_id="food_nutrition_analyzer"):
    """
    Analisa uma imagem de alimento usando a API.
    
    Args:
        image_path: Caminho para a imagem
        api_url: URL base da API
        model_id: ID do modelo a utilizar
        
    Returns:
        Resultados da análise em formato de dicionário
    """
    # Verificar se o arquivo existe
    if not os.path.exists(image_path):
        print(f"Erro: Arquivo {image_path} não encontrado")
        return None
    
    # Montar URL
    endpoint = urljoin(api_url, "analyze")
    
    # Preparar formulário
    with open(image_path, 'rb') as image_file:
        files = {"file": (os.path.basename(image_path), image_file, "image/jpeg")}
        params = {"model_id": model_id}
        
        # Enviar requisição
        print(f"Enviando imagem para análise: {image_path}")
        response = requests.post(endpoint, files=files, params=params)
    
    # Verificar resposta
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na requisição: {response.status_code}")
        print(response.text)
        return None


def print_food_analysis(analysis):
    """
    Exibe os resultados da análise de forma formatada.
    
    Args:
        analysis: Resultados da análise
    """
    if not analysis or "results" not in analysis:
        print("Nenhum resultado disponível")
        return
    
    results = analysis["results"]
    
    print("\n" + "="*50)
    print(f"ANÁLISE NUTRICIONAL DE ALIMENTOS")
    print("="*50)
    
    if "food_items" not in results:
        print("Nenhum alimento identificado na imagem")
        return
    
    print(f"Alimentos identificados: {len(results['food_items'])}")
    
    for i, item in enumerate(results["food_items"], 1):
        print(f"\n--- ALIMENTO #{i}: {item['name'].upper()} ---")
        print(f"Confiança: {item['confidence']:.1%}")
        print(f"Condição: {item['condition']}")
        
        print("\nINFORMAÇÕES NUTRICIONAIS (por 100g):")
        print(f"Calorias: {item['nutrition']['calories']} kcal")
        print(f"Proteínas: {item['nutrition']['protein']}g")
        print(f"Carboidratos: {item['nutrition']['carbs']}g")
        print(f"Gorduras: {item['nutrition']['fat']}g")
        print(f"Fibras: {item['nutrition'].get('fiber', 0)}g")
        
        print("\nMICRONUTRIENTES:")
        vitamins = ", ".join(item['nutrition'].get('vitamins', []))
        minerals = ", ".join(item['nutrition'].get('minerals', []))
        print(f"Vitaminas: {vitamins or 'N/A'}")
        print(f"Minerais: {minerals or 'N/A'}")
        
        print("\nDICAS DE SAÚDE:")
        for tip in item.get('health_tips', []):
            print(f"• {tip}")
        
        print(f"\nIMPACTO NA SAÚDE: {item['health_impact']}")
        print(f"INDICADO PARA: {', '.join(item.get('diet_type', ['N/A']))}")
    
    print("\n" + "="*50)


def register_model_if_needed():
    """
    Registra o modelo de análise nutricional se necessário.
    
    Returns:
        True se registro foi bem-sucedido, False caso contrário
    """
    try:
        from examples.food_analysis.food_nutrition_model import register_food_nutrition_model
        register_food_nutrition_model()
        return True
    except Exception as e:
        print(f"Erro ao registrar modelo: {e}")
        return False


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Cliente de exemplo para API de análise nutricional")
    parser.add_argument("image", type=str, help="Caminho para a imagem de alimento")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000/api",
                       help="URL base da API (default: http://localhost:8000/api)")
    parser.add_argument("--register", action="store_true",
                       help="Registra o modelo no Registry antes da análise")
    parser.add_argument("--raw", action="store_true",
                       help="Mostra resultados brutos em formato JSON")
    args = parser.parse_args()
    
    # Registrar modelo se solicitado
    if args.register:
        print("Registrando modelo...")
        if not register_model_if_needed():
            print("Não foi possível registrar o modelo. O serviço está executando?")
            return 1
    
    # Analisar imagem
    analysis = analyze_food_image(args.image, args.api_url)
    
    # Exibir resultados
    if analysis:
        if args.raw:
            print(json.dumps(analysis, indent=2))
        else:
            print_food_analysis(analysis)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

import os
import sys
import json

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    '..', 
    '..'
)))

from src.models.food.nutrition_service import create_food_nutrition_service
from src.exporters.nutrition_exporter import NutritionExporter

def main():
    """
    Exemplo de análise nutricional de alimentos.
    """
    # Criar serviço de análise nutricional
    nutrition_service = create_food_nutrition_service()
    
    # Diretório de recursos para imagens de exemplo
    resource_dir = os.path.join(os.path.dirname(__file__), 'resources', 'food_images')
    
    # Lista de imagens para análise
    food_images = [
        os.path.join(resource_dir, 'apple.jpg'),
        os.path.join(resource_dir, 'banana.jpg'),
        os.path.join(resource_dir, 'pizza.jpg')
    ]
    
    # Realizar análise em lote
    batch_analysis = nutrition_service.batch_analyze_foods(food_images)
    
    # Gerar relatório nutricional
    nutrition_report = nutrition_service.generate_nutrition_report(batch_analysis)
    
    # Imprimir relatório
    print(json.dumps(nutrition_report, indent=2))
    
    # Exportar resultados
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    # Exportar em diferentes formatos
    for format in ['json', 'csv', 'excel']:
        output_path = os.path.join(output_dir, f'nutrition_report.{format}')
        NutritionExporter.export(nutrition_report, output_path, format)
        print(f"Relatório exportado: {output_path}")

if __name__ == "__main__":
    main()

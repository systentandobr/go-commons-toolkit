"""
Modelo para análise nutricional de alimentos.

Este módulo implementa um modelo especializado para:
1. Identificar alimentos em imagens
2. Classificar estado do alimento (fresco, estragado, etc.)
3. Fornecer informações nutricionais
4. Avaliar impacto na saúde
"""

import os
import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from src.models.generic.generic_model import GenericModel

# Diretório base para recursos do modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
MODELS_DIR = os.path.join(os.environ.get("MODELS_DIR", "models_repository"), "food_nutrition_analyzer")


class FoodNutritionModel(GenericModel):
    """
    Modelo especializado para análise nutricional de alimentos em imagens ou vídeos.
    
    Este modelo estende o GenericModel para implementar funcionalidades específicas
    para análise de alimentos, incluindo classificação, estado e informações nutricionais.
    """
    
    def __init__(self, model_id: str = "food_nutrition_analyzer", version: str = "1.0.0"):
        """
        Inicializa o modelo de análise nutricional.
        
        Args:
            model_id: Identificador do modelo
            version: Versão do modelo
        """
        # Caminhos para recursos do modelo
        model_path = os.path.join(MODELS_DIR, "food_classifier")
        condition_model_path = os.path.join(MODELS_DIR, "food_condition_classifier")
        nutrition_db_path = os.path.join(RESOURCES_DIR, "food_nutrition_db.json")
        
        # Configurações para o modelo
        preprocessing_config = {
            "target_size": [224, 224],
            "normalize": True,
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        }
        
        postprocessing_config = {
            "top_k": 5,
            "confidence_threshold": 0.7,
            "condition_threshold": 0.6
        }
        
        # Carregar base de dados nutricional
        self.nutrition_db = self._load_nutrition_database(nutrition_db_path)
        
        # Carregar mapeamentos de classes
        class_mapping_path = os.path.join(RESOURCES_DIR, "food_classes.json")
        condition_mapping_path = os.path.join(RESOURCES_DIR, "condition_classes.json")
        
        self.food_classes = self._load_class_mapping(class_mapping_path)
        self.condition_classes = self._load_class_mapping(condition_mapping_path)
        
        # Inicializar como GenericModel
        super().__init__(
            model_id=model_id,
            version=version,
            model_path=model_path,
            task_type="classification",
            input_shape=[None, 224, 224, 3],
            preprocessing_config=preprocessing_config,
            postprocessing_config=postprocessing_config,
            metadata={
                "description": "Modelo para análise nutricional de alimentos",
                "class_labels": list(self.food_classes.values()),
                "condition_labels": list(self.condition_classes.values()),
                "input_type": "image"
            }
        )
        
        # Modelo secundário para análise de condição do alimento
        self.condition_model_path = condition_model_path
        self._condition_model = None
    
    def _load_nutrition_database(self, path: str) -> Dict[str, Dict[str, Any]]:
        """
        Carrega a base de dados nutricional.
        
        Args:
            path: Caminho para o arquivo JSON com dados nutricionais
            
        Returns:
            Dicionário mapeando alimentos para informações nutricionais
        """
        if not os.path.exists(path):
            # Criar pasta de recursos se não existir
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Criar base de dados padrão se não existir
            default_db = self._create_default_nutrition_db()
            with open(path, 'w') as f:
                json.dump(default_db, f, indent=2)
            return default_db
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def _create_default_nutrition_db(self) -> Dict[str, Dict[str, Any]]:
        """
        Cria uma base de dados nutricional padrão com alguns alimentos comuns.
        
        Returns:
            Dicionário com informações nutricionais básicas
        """
        return {
            "apple": {
                "calories": 52,
                "protein": 0.3,
                "carbs": 14,
                "fat": 0.2,
                "fiber": 2.4,
                "vitamins": ["C", "K"],
                "minerals": ["Potassium"],
                "health_tips": [
                    "Baixo teor calórico, bom para dietas",
                    "Rico em fibras e antioxidantes",
                    "Ajuda a controlar o açúcar no sangue"
                ],
                "diet_type": ["emagrecer", "saudável"]
            },
            "banana": {
                "calories": 89,
                "protein": 1.1,
                "carbs": 22.8,
                "fat": 0.3,
                "fiber": 2.6,
                "vitamins": ["B6", "C"],
                "minerals": ["Potassium", "Magnesium"],
                "health_tips": [
                    "Boa fonte de energia para atividades físicas",
                    "Ajuda na recuperação muscular",
                    "Rica em potássio, importante para pressão arterial"
                ],
                "diet_type": ["energético", "pré-treino"]
            },
            "pizza": {
                "calories": 285,
                "protein": 12,
                "carbs": 36,
                "fat": 10.4,
                "fiber": 2.5,
                "vitamins": ["A", "B12"],
                "minerals": ["Calcium", "Iron"],
                "health_tips": [
                    "Alta densidade calórica, consumo moderado",
                    "Pode conter alto teor de sódio",
                    "Versões com vegetais são mais nutritivas"
                ],
                "diet_type": ["engordar", "ocasional"]
            },
            "broccoli": {
                "calories": 34,
                "protein": 2.8,
                "carbs": 6.6,
                "fat": 0.4,
                "fiber": 2.6,
                "vitamins": ["C", "K", "A"],
                "minerals": ["Potassium", "Iron"],
                "health_tips": [
                    "Baixo teor calórico, excelente para dietas",
                    "Rico em antioxidantes e compostos anticâncer",
                    "Excelente fonte de vitamina K e C"
                ],
                "diet_type": ["emagrecer", "saudável"]
            },
            "chocolate_cake": {
                "calories": 371,
                "protein": 5.1,
                "carbs": 47.2,
                "fat": 18.8,
                "fiber": 2.1,
                "vitamins": ["B2", "E"],
                "minerals": ["Iron", "Magnesium"],
                "health_tips": [
                    "Alto teor calórico, consumo ocasional",
                    "Rico em açúcares refinados",
                    "Versões com cacau escuro têm mais antioxidantes"
                ],
                "diet_type": ["engordar", "ocasional"]
            }
        }
    
    def _load_class_mapping(self, path: str) -> Dict[int, str]:
        """
        Carrega o mapeamento de classes (IDs para nomes).
        
        Args:
            path: Caminho para o arquivo JSON com mapeamento
            
        Returns:
            Dicionário mapeando IDs para nomes de classes
        """
        if not os.path.exists(path):
            # Criar pasta de recursos se não existir
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Criar mapeamento padrão se não existir
            if "condition" in path:
                default_mapping = self._create_default_condition_mapping()
            else:
                default_mapping = self._create_default_food_mapping()
                
            with open(path, 'w') as f:
                json.dump(default_mapping, f, indent=2)
            return default_mapping
        
        with open(path, 'r') as f:
            mapping = json.load(f)
            # Converter chaves de string para int
            return {int(k): v for k, v in mapping.items()}
    
    def _create_default_food_mapping(self) -> Dict[int, str]:
        """
        Cria um mapeamento padrão para classes de alimentos.
        
        Returns:
            Dicionário mapeando IDs para nomes de alimentos
        """
        return {
            0: "apple",
            1: "banana",
            2: "broccoli",
            3: "burger",
            4: "cake",
            5: "carrot",
            6: "hot_dog",
            7: "orange",
            8: "pizza",
            9: "salad"
        }
    
    def _create_default_condition_mapping(self) -> Dict[int, str]:
        """
        Cria um mapeamento padrão para condições de alimentos.
        
        Returns:
            Dicionário mapeando IDs para estados de alimentos
        """
        return {
            0: "fresh",
            1: "spoiled",
            2: "unripe",
            3: "overripe",
            4: "cooked",
            5: "burnt",
            6: "frozen",
            7: "moldy"
        }
    
    def _post_load_setup(self) -> None:
        """
        Configura componentes adicionais após carregar o modelo principal.
        
        Esta função é chamada após o modelo principal ser carregado.
        """
        super()._post_load_setup()
        
        # Carregar modelo de condição do alimento
        if self._condition_model is None and hasattr(self, '_context'):
            try:
                self._condition_model = self._context.load_model(self.condition_model_path)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar modelo de condição: {e}")
    
    def analyze_food_condition(self, image: tf.Tensor, food_class: str) -> Dict[str, Any]:
        """
        Analisa a condição (fresco, estragado, etc.) de um alimento.
        
        Args:
            image: Imagem pré-processada
            food_class: Classe do alimento identificado
            
        Returns:
            Dicionário com condição do alimento e confiança
        """
        if self._condition_model is None:
            # Retornar valor padrão se modelo não disponível
            return {"condition": "unknown", "confidence": 0.0}
        
        # Fazer predição com modelo de condição
        condition_output = self._context.run_inference(self._condition_model, image)
        
        # Processar saída
        condition_probs = tf.nn.softmax(condition_output, axis=-1).numpy()[0]
        condition_id = np.argmax(condition_probs)
        confidence = float(condition_probs[condition_id])
        
        # Obter nome da condição
        condition_name = self.condition_classes.get(condition_id, "unknown")
        
        return {
            "condition": condition_name,
            "confidence": confidence
        }
    
    def get_nutrition_info(self, food_class: str) -> Dict[str, Any]:
        """
        Obtém informações nutricionais para um alimento.
        
        Args:
            food_class: Classe do alimento
            
        Returns:
            Dicionário com informações nutricionais
        """
        # Buscar na base de dados
        if food_class in self.nutrition_db:
            return self.nutrition_db[food_class]
        
        # Retornar valores padrão se não encontrado
        return {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "fiber": 0,
            "vitamins": [],
            "minerals": [],
            "health_tips": ["Informações nutricionais não disponíveis"],
            "diet_type": ["desconhecido"]
        }
    
    def analyze_health_impact(self, nutrition_info: Dict[str, Any], condition: str) -> str:
        """
        Analisa o impacto na saúde com base nas informações nutricionais.
        
        Args:
            nutrition_info: Informações nutricionais do alimento
            condition: Condição do alimento
            
        Returns:
            String com avaliação do impacto na saúde
        """
        # Verificar condição primeiro
        if condition in ["spoiled", "moldy", "burnt"]:
            return "Não recomendado para consumo devido à condição"
        
        # Análise baseada em valor nutricional
        diet_type = nutrition_info.get("diet_type", ["desconhecido"])[0]
        calories = nutrition_info.get("calories", 0)
        
        if diet_type == "emagrecer":
            return "Recomendado para dietas de emagrecimento"
        elif diet_type == "engordar":
            return "Alto valor calórico, modere o consumo em dietas"
        elif diet_type == "saudável":
            return "Alimento nutritivo com bom perfil nutricional"
        elif diet_type == "energético":
            return "Bom para fornecer energia antes de atividades"
        elif diet_type == "ocasional":
            return "Consumo ocasional recomendado"
        else:
            # Análise baseada em calorias se não houver tipo específico
            if calories < 50:
                return "Baixo teor calórico, bom para dietas de controle de peso"
            elif calories < 150:
                return "Valor calórico moderado, adequado para alimentação balanceada"
            else:
                return "Alto valor calórico, consumo moderado recomendado"
    
    def postprocess(self, outputs: Any) -> Dict[str, Any]:
        """
        Processa a saída do modelo e gera análise nutricional completa.
        
        Args:
            outputs: Saída do modelo de classificação
            
        Returns:
            Dicionário com análise completa dos alimentos
        """
        # Processar classificação básica usando GenericModel
        base_results = super().postprocess(outputs)
        
        # Extrair previsões
        if "predictions" not in base_results:
            return {"error": "Falha na classificação", "food_items": []}
        
        predictions = base_results["predictions"]
        
        # Formatar resultados por alimento
        food_items = []
        
        for pred in predictions:
            # Obter classe e confiança
            food_class = pred["class_name"].lower()
            confidence = pred["confidence"]
            
            # Analisar condição do alimento usando o modelo secundário
            # Estamos usando a mesma imagem para analisar a condição
            condition_result = self.analyze_food_condition(outputs, food_class)
            
            # Obter informações nutricionais
            nutrition_info = self.get_nutrition_info(food_class)
            
            # Analisar impacto na saúde
            health_impact = self.analyze_health_impact(nutrition_info, condition_result["condition"])
            
            # Criar item de alimento formatado
            food_item = {
                "name": food_class,
                "confidence": confidence,
                "condition": condition_result["condition"],
                "condition_confidence": condition_result["confidence"],
                "nutrition": {
                    "calories": nutrition_info["calories"],
                    "protein": nutrition_info["protein"],
                    "carbs": nutrition_info["carbs"],
                    "fat": nutrition_info["fat"],
                    "fiber": nutrition_info.get("fiber", 0),
                    "vitamins": nutrition_info.get("vitamins", []),
                    "minerals": nutrition_info.get("minerals", [])
                },
                "health_tips": nutrition_info.get("health_tips", []),
                "diet_type": nutrition_info.get("diet_type", ["desconhecido"]),
                "health_impact": health_impact
            }
            
            food_items.append(food_item)
        
        # Adicionar informações sobre a quantidade de itens encontrados
        return {
            "food_items": food_items,
            "count": len(food_items),
            "analysis_version": self.version
        }


# Função para criar e registrar o modelo
def register_food_nutrition_model():
    """
    Cria e registra o modelo de análise nutricional no ModelRegistry.
    
    Returns:
        Instância do modelo FoodNutritionModel
    """
    from src.core.registry import ModelRegistry
    
    # Criar modelo
    model = FoodNutritionModel()
    
    # Registrar no registry global
    registry = ModelRegistry()
    registry.register_model(model)
    
    return model


if __name__ == "__main__":
    """Script para teste do modelo."""
    model = register_food_nutrition_model()
    print(f"Modelo {model.model_id}@{model.version} registrado com sucesso!")

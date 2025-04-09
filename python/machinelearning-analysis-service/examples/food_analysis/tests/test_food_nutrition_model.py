"""
Testes para o modelo de análise nutricional de alimentos.
"""

import os
import sys
import pytest
import numpy as np
import tensorflow as tf

# Configurar path para incluir a raiz do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from examples.food_analysis.food_nutrition_model import FoodNutritionModel


class TestFoodNutritionModel:
    """Testes para a classe FoodNutritionModel."""
    
    @pytest.fixture
    def model(self):
        """Fixture para criar instância do modelo."""
        return FoodNutritionModel()
    
    def test_init(self, model):
        """Testa a inicialização do modelo."""
        assert model.model_id == "food_nutrition_analyzer"
        assert model.version == "1.0.0"
        assert model.task_type == "classification"
    
    def test_nutrition_db_loaded(self, model):
        """Testa se a base de dados nutricional foi carregada."""
        assert model.nutrition_db is not None
        assert isinstance(model.nutrition_db, dict)
        assert len(model.nutrition_db) > 0
        
        # Verificar se contém pelo menos alguns alimentos comuns
        for food in ["apple", "banana", "pizza"]:
            assert food in model.nutrition_db
    
    def test_class_mappings_loaded(self, model):
        """Testa se os mapeamentos de classes foram carregados."""
        assert model.food_classes is not None
        assert model.condition_classes is not None
        assert isinstance(model.food_classes, dict)
        assert isinstance(model.condition_classes, dict)
    
    def test_get_nutrition_info(self, model):
        """Testa a função de obtenção de informações nutricionais."""
        # Verificar alimento existente
        apple_info = model.get_nutrition_info("apple")
        assert apple_info is not None
        assert apple_info["calories"] > 0
        assert "protein" in apple_info
        assert "carbs" in apple_info
        assert "fat" in apple_info
        
        # Verificar alimento inexistente (deve retornar valores padrão)
        unknown_info = model.get_nutrition_info("nonexistent_food")
        assert unknown_info is not None
        assert unknown_info["calories"] == 0
        assert unknown_info["protein"] == 0
    
    def test_analyze_health_impact(self, model):
        """Testa a análise de impacto na saúde."""
        # Verificar impacto para alimentos em boas condições
        nutrition_info = model.get_nutrition_info("apple")
        impact = model.analyze_health_impact(nutrition_info, "fresh")
        assert impact is not None
        assert isinstance(impact, str)
        assert len(impact) > 0
        
        # Verificar impacto para alimentos em más condições
        impact_bad = model.analyze_health_impact(nutrition_info, "moldy")
        assert "Não recomendado" in impact_bad
    
    def test_preprocess(self, model):
        """Testa o pré-processamento de imagens."""
        # Criar imagem de teste
        test_image = np.random.randint(0, 256, (100, 100, 3)).astype(np.uint8)
        
        # Pré-processar
        processed = model.preprocess(test_image)
        
        # Verificar tamanho e normalização
        assert isinstance(processed, tf.Tensor)
        assert processed.shape[1:3] == tuple(model.preprocessing_config["target_size"])
        assert tf.reduce_max(processed) <= 1.0
    
    def test_postprocess(self, model, monkeypatch):
        """Testa o pós-processamento dos resultados."""
        # Mock para a função de predição
        def mock_process_single_classification(self, output):
            return {
                "predictions": [
                    {"class_name": "apple", "confidence": 0.9},
                    {"class_name": "banana", "confidence": 0.05}
                ]
            }
        
        # Mock para a função de análise de condição
        def mock_analyze_food_condition(self, image, food_class):
            return {"condition": "fresh", "confidence": 0.85}
        
        # Aplicar mocks
        monkeypatch.setattr(FoodNutritionModel, "_process_single_classification", 
                           mock_process_single_classification)
        monkeypatch.setattr(FoodNutritionModel, "analyze_food_condition",
                           mock_analyze_food_condition)
        
        # Simular saída do modelo
        mock_output = tf.constant([[0.1, 0.9, 0.0, 0.0]])
        
        # Processar resultados
        results = model.postprocess(mock_output)
        
        # Verificar estrutura e conteúdo dos resultados
        assert "food_items" in results
        assert len(results["food_items"]) > 0
        assert results["count"] == len(results["food_items"])
        
        food_item = results["food_items"][0]
        assert food_item["name"] == "apple"
        assert "confidence" in food_item
        assert "condition" in food_item
        assert "nutrition" in food_item
        assert "health_impact" in food_item

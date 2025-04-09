import os
import json
import numpy as np
import tensorflow as tf
from typing import Dict, Any, List, Optional

from ...core.protocols import ModelProtocol
from .protocols import NutritionInfo, FoodAnalysisProtocol

class FoodDetectionModel(ModelProtocol, FoodAnalysisProtocol):
    """
    Modelo especializado para detecção e análise de alimentos.
    
    Implementa os protocolos de ModelProtocol e FoodAnalysisProtocol
    para fornecer análise completa de alimentos em imagens.
    """
    
    def __init__(
        self, 
        model_id: str = "food_detection", 
        version: str = "1.0.0",
        model_path: str = None,
        nutrition_db_path: str = None,
        classes_path: str = None
    ):
        """
        Inicializa o modelo de detecção de alimentos.
        
        Args:
            model_id: Identificador único do modelo
            version: Versão do modelo
            model_path: Caminho para o modelo de machine learning
            nutrition_db_path: Caminho para o banco de dados nutricional
            classes_path: Caminho para mapeamento de classes
        """
        self.model_id = model_id
        self.version = version
        self._model = None
        
        # Caminhos para recursos
        self._model_path = model_path or self._get_default_model_path()
        self._nutrition_db_path = nutrition_db_path or self._get_default_nutrition_db_path()
        self._classes_path = classes_path or self._get_default_classes_path()
        
        # Carregar recursos
        self._nutrition_db = self._load_nutrition_database()
        self._food_classes = self._load_food_classes()
    
    def _get_default_model_path(self) -> str:
        """
        Obtém o caminho padrão para o modelo de detecção.
        
        Returns:
            Caminho para o modelo
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "..", "..", "..", "models_repository", "food_detection")
    
    def _get_default_nutrition_db_path(self) -> str:
        """
        Obtém o caminho padrão para o banco de dados nutricional.
        
        Returns:
            Caminho para o banco de dados nutricional
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "resources", "nutrition_database.json")
    
    def _get_default_classes_path(self) -> str:
        """
        Obtém o caminho padrão para mapeamento de classes.
        
        Returns:
            Caminho para o arquivo de classes
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "resources", "food_classes.json")
    
    def _load_nutrition_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Carrega o banco de dados nutricional.
        
        Returns:
            Dicionário com informações nutricionais
        """
        os.makedirs(os.path.dirname(self._nutrition_db_path), exist_ok=True)
        
        if not os.path.exists(self._nutrition_db_path):
            # Criar banco de dados padrão
            default_db = self._create_default_nutrition_db()
            with open(self._nutrition_db_path, 'w') as f:
                json.dump(default_db, f, indent=2)
            return default_db
        
        with open(self._nutrition_db_path, 'r') as f:
            return json.load(f)
    
    def _create_default_nutrition_db(self) -> Dict[str, Dict[str, Any]]:
        """
        Cria um banco de dados nutricional padrão.
        
        Returns:
            Dicionário com informações nutricionais básicas
        """
        return {
            "apple": {
                "name": "Maçã",
                "calories": 52,
                "proteins": 0.3,
                "carbohydrates": 14,
                "fats": 0.2,
                "fiber": 2.4,
                "vitamins": ["C", "K"],
                "minerals": ["Potássio"],
                "health_tips": [
                    "Baixo teor calórico, bom para dietas",
                    "Rico em fibras e antioxidantes"
                ]
            },
            "banana": {
                "name": "Banana",
                "calories": 89,
                "proteins": 1.1,
                "carbohydrates": 22.8,
                "fats": 0.3,
                "fiber": 2.6,
                "vitamins": ["B6", "C"],
                "minerals": ["Potássio", "Magnésio"],
                "health_tips": [
                    "Boa fonte de energia",
                    "Ajuda na recuperação muscular"
                ]
            }
        }
    
    def _load_food_classes(self) -> Dict[int, str]:
        """
        Carrega o mapeamento de classes de alimentos.
        
        Returns:
            Dicionário mapeando IDs para nomes de classes
        """
        os.makedirs(os.path.dirname(self._classes_path), exist_ok=True)
        
        if not os.path.exists(self._classes_path):
            # Criar mapeamento padrão
            default_classes = {
                0: "apple",
                1: "banana",
                2: "orange",
                3: "broccoli",
                4: "pizza"
            }
            with open(self._classes_path, 'w') as f:
                json.dump(default_classes, f, indent=2)
            return default_classes
        
        with open(self._classes_path, 'r') as f:
            return {int(k): v for k, v in json.load(f).items()}
    
    def preprocess(self, inputs: Any) -> np.ndarray:
        """
        Pré-processa a imagem para o modelo.
        
        Args:
            inputs: Imagem de entrada (caminho ou array)
        
        Returns:
            Imagem pré-processada
        """
        # Carregar imagem
        if isinstance(inputs, str):
            image = tf.keras.preprocessing.image.load_img(inputs, target_size=(224, 224))
        elif isinstance(inputs, np.ndarray):
            image = tf.image.resize(inputs, (224, 224))
        else:
            raise ValueError(f"Tipo de entrada não suportado: {type(inputs)}")
        
        # Converter para array e normalizar
        image_array = tf.keras.preprocessing.image.img_to_array(image)
        image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)
        
        return image_array
    
    def predict(self, inputs: np.ndarray) -> np.ndarray:
        """
        Executa predição no modelo.
        
        Args:
            inputs: Imagem pré-processada
        
        Returns:
            Predições do modelo
        """
        # Verificar se o modelo foi carregado
        if self._model is None:
            self._model = tf.keras.models.load_model(self._model_path)
        
        # Adicionar dimensão de batch
        inputs_batch = np.expand_dims(inputs, axis=0)
        
        # Executar predição
        return self._model.predict(inputs_batch)
    
    def postprocess(self, outputs: np.ndarray) -> Dict[str, Any]:
        """
        Processa as saídas do modelo.
        
        Args:
            outputs: Predições do modelo
        
        Returns:
            Resultados processados
        """
        # Aplicar softmax para obter probabilidades
        probabilities = tf.nn.softmax(outputs, axis=-1).numpy()[0]
        
        # Encontrar as 3 melhores classes
        top_k_indices = probabilities.argsort()[-3:][::-1]
        
        predictions = []
        for idx in top_k_indices:
            class_name = self._food_classes.get(idx, f"unknown_{idx}")
            confidence = float(probabilities[idx])
            
            predictions.append({
                "class_name": class_name,
                "confidence": confidence
            })
        
        return {
            "predictions": predictions,
            "top_prediction": predictions[0] if predictions else None
        }
    
    def classify_food(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Classifica o tipo de alimento na imagem.
        
        Args:
            image: Imagem pré-processada
        
        Returns:
            Dicionário com informações da classificação
        """
        # Pré-processar imagem se necessário
        if not isinstance(image, np.ndarray):
            image = self.preprocess(image)
        
        # Executar predição
        outputs = self.predict(image)
        
        # Processar resultados
        result = self.postprocess(outputs)
        
        return result
    
    def assess_food_condition(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Avalia a condição do alimento.
        
        Args:
            image: Imagem pré-processada
        
        Returns:
            Dicionário com estado e confiança do alimento
        """
        # Implementação simplificada
        return {
            "condition": "fresh",
            "confidence": 0.95,
            "reasons": [
                "Sem sinais visíveis de deterioração",
                "Cor e textura uniformes"
            ]
        }
    
    def get_nutrition_info(self, food_class: str) -> NutritionInfo:
        """
        Obtém informações nutricionais de um alimento.
        
        Args:
            food_class: Classe do alimento
        
        Returns:
            Objeto com informações nutricionais
        """
        # Buscar no banco de dados
        nutrition_data = self._nutrition_db.get(food_class, {})
        
        return NutritionInfo(
            name=nutrition_data.get('name', food_class),
            calories=nutrition_data.get('calories', 0),
            proteins=nutrition_data.get('proteins', 0),
            carbohydrates=nutrition_data.get('carbohydrates', 0),
            fats=nutrition_data.get('fats', 0),
            fiber=nutrition_data.get('fiber', 0),
            vitamins=nutrition_data.get('vitamins', []),
            minerals=nutrition_data.get('minerals', []),
            health_tips=nutrition_data.get('health_tips', [])
        )
    
    def analyze_health_impact(self, nutrition_info: NutritionInfo) -> str:
        """
        Analisa o impacto do alimento na saúde.
        
        Args:
            nutrition_info: Informações nutricionais do alimento
        
        Returns:
            Descrição do impacto na saúde
        """
        # Análise baseada em calorias e nutrientes
        if nutrition_info.calories < 50:
            return "Baixo teor calórico, ideal para dietas de emagrecimento"
        elif nutrition_info.calories < 150:
            return "Valor calórico moderado, recomendado para alimentação balanceada"
        else:
            return "Alto valor calórico, consumo moderado recomendado"

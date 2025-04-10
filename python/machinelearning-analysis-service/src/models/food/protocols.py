from typing import Protocol, Dict, Any, List
from dataclasses import dataclass, field
import numpy as np

@dataclass
class NutritionInfo:
    """
    Classe de dados para informações nutricionais detalhadas.
    """
    name: str
    calories: float
    proteins: float
    carbohydrates: float
    fats: float
    fiber: float = 0.0
    vitamins: List[str] = field(default_factory=list)
    minerals: List[str] = field(default_factory=list)
    health_tips: List[str] = field(default_factory=list)

class FoodAnalysisProtocol(Protocol):
    """
    Protocolo para análise de alimentos em imagens.
    Define métodos essenciais para classificação, 
    análise nutricional e estado do alimento.
    """
    
    def classify_food(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Classifica o tipo de alimento na imagem.
        
        Args:
            image: Imagem pré-processada
        
        Returns:
            Dicionário com informações da classificação
        """
        ...
    
    def assess_food_condition(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Avalia a condição do alimento.
        
        Args:
            image: Imagem pré-processada
        
        Returns:
            Dicionário com estado e confiança do alimento
        """
        ...
    
    def get_nutrition_info(self, food_class: str) -> NutritionInfo:
        """
        Obtém informações nutricionais de um alimento.
        
        Args:
            food_class: Classe do alimento
        
        Returns:
            Objeto com informações nutricionais
        """
        ...
    
    def analyze_health_impact(self, nutrition_info: NutritionInfo) -> str:
        """
        Analisa o impacto do alimento na saúde.
        
        Args:
            nutrition_info: Informações nutricionais do alimento
        
        Returns:
            Descrição do impacto na saúde
        """
        ...

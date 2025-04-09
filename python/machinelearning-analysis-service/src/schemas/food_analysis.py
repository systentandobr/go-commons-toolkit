from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class NutritionData(BaseModel):
    """
    Modelo de dados para informações nutricionais de um alimento.
    """
    calories: float = Field(..., description="Quantidade de calorias")
    proteins: float = Field(0, description="Quantidade de proteínas")
    carbohydrates: float = Field(0, description="Quantidade de carboidratos")
    fats: float = Field(0, description="Quantidade de gorduras")
    fiber: float = Field(0, description="Quantidade de fibras")
    vitamins: List[str] = Field(default_factory=list, description="Vitaminas presentes")
    minerals: List[str] = Field(default_factory=list, description="Minerais presentes")

class FoodClassification(BaseModel):
    """
    Modelo de dados para classificação de alimentos.
    """
    food_class: str = Field(..., description="Classe do alimento identificado")
    confidence: float = Field(..., description="Confiança da classificação", ge=0, le=1)

class FoodCondition(BaseModel):
    """
    Modelo de dados para condição do alimento.
    """
    status: str = Field(..., description="Status do alimento (fresco, estragado, etc)")
    confidence: float = Field(..., description="Confiança da avaliação", ge=0, le=1)
    reasons: List[str] = Field(default_factory=list, description="Razões para a avaliação")

class FoodAnalysisResponse(BaseModel):
    """
    Modelo de resposta para análise completa de um alimento.
    """
    status: str = Field(..., description="Status da análise")
    food_classification: Optional[FoodClassification] = Field(None, description="Classificação do alimento")
    nutrition: Optional[NutritionData] = Field(None, description="Informações nutricionais")
    condition: Optional[FoodCondition] = Field(None, description="Condição do alimento")
    health_impact: Optional[str] = Field(None, description="Impacto na saúde")
    health_tips: List[str] = Field(default_factory=list, description="Dicas de saúde")
    error: Optional[str] = Field(None, description="Mensagem de erro em caso de falha")

class BatchFoodAnalysisResponse(BaseModel):
    """
    Modelo de resposta para análise em lote de alimentos.
    """
    total_analyzed: int = Field(..., description="Total de imagens analisadas")
    successful_analyses: List[FoodAnalysisResponse] = Field(
        ..., 
        description="Lista de análises realizadas com sucesso"
    )
    failed_analyses: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Lista de análises que falharam"
    )
    nutrition_summary: Optional[Dict[str, Any]] = Field(
        None, 
        description="Resumo nutricional das análises"
    )

class NutritionReportResponse(BaseModel):
    """
    Modelo de resposta para relatório nutricional consolidado.
    """
    status: str = Field(..., description="Status do relatório")
    total_foods_analyzed: int = Field(..., description="Total de alimentos analisados")
    total_nutrition: NutritionData = Field(..., description="Total de nutrientes")
    recommendations: List[str] = Field(
        default_factory=list, 
        description="Recomendações nutricionais"
    )
    food_details: List[FoodAnalysisResponse] = Field(
        ..., 
        description="Detalhes de cada análise de alimento"
    )

import os
import typing
from typing import Dict, Any, List, Optional

from ...core.protocols import ModelContextProtocol
from ...core.registry import ModelRegistry
from .detection_model import FoodDetectionModel
from .protocols import NutritionInfo, FoodAnalysisProtocol

class FoodNutritionContext:
    """
    Contexto específico para análise nutricional de alimentos.
    Implementa o ExecutionContextProtocol.
    """
    def __init__(self, model: FoodDetectionModel):
        """
        Inicializa o contexto de análise nutricional.
        
        Args:
            model: Modelo de detecção de alimentos
        """
        self._model = model
    
    def load_model(self, model_path: str) -> Any:
        """
        Carrega o modelo de detecção de alimentos.
        
        Args:
            model_path: Caminho para o modelo
        
        Returns:
            Modelo carregado
        """
        return self._model
    
    def run_inference(self, model: Any, inputs: Any) -> Any:
        """
        Executa inferência no modelo.
        
        Args:
            model: Modelo de detecção
            inputs: Dados de entrada para análise
        
        Returns:
            Resultados da inferência
        """
        return model.predict(inputs)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Obtém metadados do contexto de execução.
        
        Returns:
            Dicionário com metadados
        """
        return {
            "context_type": "food_nutrition",
            "model_id": self._model.model_id,
            "model_version": self._model.version
        }

class FoodNutritionService(ModelContextProtocol):
    """
    Serviço de análise nutricional implementando ModelContextProtocol.
    
    Responsável por orquestrar a análise completa de alimentos,
    integrando detecção, classificação e avaliação nutricional.
    """
    
    def __init__(
        self, 
        model: Optional[FoodDetectionModel] = None,
        model_registry: Optional[ModelRegistry] = None
    ):
        """
        Inicializa o serviço de análise nutricional.
        
        Args:
            model: Modelo de detecção de alimentos (opcional)
            model_registry: Registro de modelos (opcional)
        """
        # Usar registro de modelos ou criar um novo
        self._model_registry = model_registry or ModelRegistry()
        
        # Usar modelo fornecido ou carregar do registro
        if model:
            self._detection_model = model
        else:
            self._detection_model = self._load_default_model()
        
        # Criar contexto de execução
        self._context = FoodNutritionContext(self._detection_model)
    
    def _load_default_model(self) -> FoodDetectionModel:
        """
        Carrega o modelo padrão de detecção de alimentos.
        
        Returns:
            Modelo de detecção de alimentos
        """
        try:
            # Tentar obter modelo do registro
            model_context = self._model_registry.create_model_context(
                model_id="food_detection", 
                version="1.0.0"
            )
            
            if model_context:
                return model_context.model
        except Exception:
            pass
        
        # Criar modelo padrão se não encontrado no registro
        return FoodDetectionModel()
    
    def analyze(self, inputs: Any) -> Dict[str, Any]:
        """
        Executa análise completa de alimentos seguindo o ModelContextProtocol.
        
        Args:
            inputs: Imagem ou caminho da imagem para análise
        
        Returns:
            Resultados da análise nutricional
        """
        try:
            # Pré-processamento
            processed_inputs = self._detection_model.preprocess(inputs)
            
            # Inferência
            raw_outputs = self._detection_model.predict(processed_inputs)
            
            # Pós-processamento
            results = self._detection_model.postprocess(raw_outputs)
            
            # Adicionar informações nutricionais detalhadas
            if results.get('top_prediction'):
                food_class = results['top_prediction']['class_name']
                nutrition_info = self._detection_model.get_nutrition_info(food_class)
                
                # Avaliar condição do alimento
                food_condition = self._detection_model.assess_food_condition(processed_inputs)
                
                # Analisar impacto na saúde
                health_impact = self._detection_model.analyze_health_impact(nutrition_info)
                
                # Enriquecer resultados
                results.update({
                    'nutrition': {
                        'name': nutrition_info.name,
                        'calories': nutrition_info.calories,
                        'proteins': nutrition_info.proteins,
                        'carbohydrates': nutrition_info.carbohydrates,
                        'fats': nutrition_info.fats,
                        'fiber': nutrition_info.fiber,
                        'vitamins': nutrition_info.vitamins,
                        'minerals': nutrition_info.minerals
                    },
                    'health_impact': health_impact,
                    'condition': food_condition
                })
            
            # Adicionar metadados
            results['metadata'] = {
                'model_id': self._detection_model.model_id,
                'model_version': self._detection_model.version,
                'context': self._context.get_metadata()
            }
            
            return results
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'metadata': {
                    'model_id': self._detection_model.model_id,
                    'model_version': self._detection_model.version
                }
            }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o modelo e contexto.
        
        Returns:
            Dicionário com informações do modelo
        """
        return {
            'model': {
                'id': self._detection_model.model_id,
                'version': self._detection_model.version
            },
            'context': self._context.get_metadata()
        }
    
    def batch_analyze_foods(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Analisa múltiplas imagens de alimentos em lote.
        
        Args:
            image_paths: Lista de caminhos para imagens de alimentos a serem analisadas
        
        Returns:
            Lista de resultados de análise para cada imagem
        """
        results = []
        
        for image_path in image_paths:
            try:
                # Analisar cada imagem individualmente
                food_analysis = self.analyze(image_path)
                
                # Adicionar caminho da imagem ao resultado
                food_analysis['image_path'] = image_path
                
                # Adicionar nome do alimento como identificador
                if 'top_prediction' in food_analysis:
                    food_analysis['food_name'] = food_analysis['top_prediction']['class_name']
                
                results.append(food_analysis)
            except Exception as e:
                # Em caso de erro, adicionar resultado com erro
                results.append({
                    'status': 'error',
                    'message': f"Erro ao analisar {image_path}: {str(e)}",
                    'image_path': image_path
                })
        
        return results
    
    def generate_nutrition_report(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera um relatório nutricional a partir dos resultados de análise em lote.
        
        Args:
            batch_results: Resultados da análise em lote obtidos por batch_analyze_foods
        
        Returns:
            Relatório nutricional consolidado
        """
        # Inicializar estrutura do relatório
        report = {
            'food_details': [],
            'total_nutrition': {
                'calories': 0,
                'proteins': 0,
                'carbohydrates': 0,
                'fats': 0,
                'fiber': 0
            },
            'recommendations': [],
            'metadata': {
                'total_items': len(batch_results),
                'successful_analyses': 0,
                'failed_analyses': 0
            }
        }
        
        # Processar cada resultado
        for food_result in batch_results:
            # Verificar se a análise foi bem-sucedida
            if food_result.get('status') == 'error':
                report['metadata']['failed_analyses'] += 1
                continue
            
            report['metadata']['successful_analyses'] += 1
            
            # Extrair detalhes nutricionais
            food_detail = {
                'food_classification': {
                    'food_class': food_result.get('top_prediction', {}).get('class_name', 'Desconhecido'),
                    'confidence': food_result.get('top_prediction', {}).get('confidence', 0)
                },
                'nutrition': food_result.get('nutrition', {}),
                'health_impact': food_result.get('health_impact', 'Não avaliado'),
                'condition': food_result.get('condition', {'status': 'Não verificado'}),
                'image_path': food_result.get('image_path', '')
            }
            
            # Adicionar aos detalhes
            report['food_details'].append(food_detail)
            
            # Somar ao total nutricional
            nutrition = food_result.get('nutrition', {})
            report['total_nutrition']['calories'] += nutrition.get('calories', 0)
            report['total_nutrition']['proteins'] += nutrition.get('proteins', 0)
            report['total_nutrition']['carbohydrates'] += nutrition.get('carbohydrates', 0)
            report['total_nutrition']['fats'] += nutrition.get('fats', 0)
            report['total_nutrition']['fiber'] += nutrition.get('fiber', 0)
        
        # Gerar recomendações baseadas nos totais
        self._generate_diet_recommendations(report)
        
        return report
    
    def _generate_diet_recommendations(self, report: Dict[str, Any]) -> None:
        """
        Gera recomendações dietéticas baseadas na análise nutricional.
        
        Args:
            report: Relatório nutricional a ser atualizado com recomendações
        """
        total = report['total_nutrition']
        recommendations = []
        
        # Verificações básicas de macronutrientes
        if total['calories'] > 2500:
            recommendations.append("O consumo calórico está elevado. Considere reduzir a ingestão calórica total.")
        
        if total['fats'] > 70:
            recommendations.append("O consumo de gorduras está acima do recomendado. Priorize gorduras saudáveis e reduza gorduras saturadas.")
        
        if total['carbohydrates'] > 300:
            recommendations.append("O consumo de carboidratos está elevado. Opte por carboidratos complexos e reduza açúcares simples.")
        
        if total['proteins'] < 50:
            recommendations.append("O consumo de proteínas está abaixo do ideal. Considere incluir mais fontes proteicas na dieta.")
        
        if total['fiber'] < 25:
            recommendations.append("O consumo de fibras está abaixo do recomendado. Aumente a ingestão de vegetais, frutas e grãos integrais.")
        
        # Verificações baseadas na composição da dieta
        fruit_count = len([food for food in report['food_details'] 
                         if 'fruit' in food['food_classification']['food_class'].lower()])
        
        vegetable_count = len([food for food in report['food_details'] 
                             if 'vegetable' in food['food_classification']['food_class'].lower()])
        
        if fruit_count + vegetable_count < 2:
            recommendations.append("Consumo baixo de frutas e vegetais. Recomenda-se pelo menos 5 porções diárias.")
        
        # Adicionar recomendações gerais se não houver específicas
        if not recommendations:
            recommendations.append("Seu perfil nutricional parece equilibrado. Mantenha a variedade de alimentos e a hidratação adequada.")
        
        # Atualizar o relatório
        report['recommendations'] = recommendations

def create_food_nutrition_service() -> FoodNutritionService:
    """
    Função de fábrica para criar o serviço de análise nutricional.
    
    Returns:
        Instância do serviço de análise nutricional
    """
    # Registrar modelo no serviço
    model_registry = ModelRegistry()
    food_detection_model = FoodDetectionModel()
    model_registry.register_model(food_detection_model)
    
    return FoodNutritionService(
        model=food_detection_model, 
        model_registry=model_registry
    )

# Registrar serviço no registro de modelos (opcional)
def register_food_nutrition_service():
    """
    Registra o serviço de análise nutricional no registro de modelos.
    """
    model_registry = ModelRegistry()
    service = create_food_nutrition_service()
    model_registry.register_model(service)
    return service

# Registro automático ao importar
if __name__ == "__main__":
    register_food_nutrition_service()

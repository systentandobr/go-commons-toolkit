import json
import csv
import pandas as pd
from typing import Dict, List, Any
from .exporter_base import ExporterBase

class NutritionExporter(ExporterBase):
    """
    Exportador especializado para resultados de análise nutricional.
    """
    
    def export_json(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Exporta dados nutricionais para JSON.
        
        Args:
            data: Dados de análise nutricional
            output_path: Caminho para salvar o arquivo
        
        Returns:
            Caminho do arquivo exportado
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return output_path
    
    def export_csv(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Exporta dados nutricionais para CSV.
        
        Args:
            data: Dados de análise nutricional
            output_path: Caminho para salvar o arquivo
        
        Returns:
            Caminho do arquivo exportado
        """
        # Verificar se há detalhes de alimentos
        if 'food_details' not in data:
            raise ValueError("Dados não contêm informações de alimentos")
        
        # Preparar lista de dados para DataFrame
        rows = []
        for food_analysis in data.get('food_details', []):
            row = {
                'food_class': food_analysis.get('food_classification', {}).get('food_class', 'Desconhecido'),
                'confidence': food_analysis.get('food_classification', {}).get('confidence', 0),
                'calories': food_analysis.get('nutrition', {}).get('calories', 0),
                'proteins': food_analysis.get('nutrition', {}).get('proteins', 0),
                'carbohydrates': food_analysis.get('nutrition', {}).get('carbohydrates', 0),
                'fats': food_analysis.get('nutrition', {}).get('fats', 0),
                'fiber': food_analysis.get('nutrition', {}).get('fiber', 0),
                'health_impact': food_analysis.get('health_impact', 'Não avaliado'),
                'food_condition': food_analysis.get('condition', {}).get('status', 'Não verificado')
            }
            rows.append(row)
        
        # Criar DataFrame
        df = pd.DataFrame(rows)
        
        # Adicionar resumo nutricional como linhas extras
        if 'total_nutrition' in data:
            total_row = {
                'food_class': 'TOTAL',
                'calories': data['total_nutrition'].get('calories', 0),
                'proteins': data['total_nutrition'].get('proteins', 0),
                'carbohydrates': data['total_nutrition'].get('carbohydrates', 0),
                'fats': data['total_nutrition'].get('fats', 0)
            }
            df = df.append(total_row, ignore_index=True)
        
        # Adicionar recomendações como linhas extras
        if 'recommendations' in data:
            for recommendation in data.get('recommendations', []):
                df = df.append({
                    'food_class': 'RECOMENDAÇÃO',
                    'health_impact': recommendation
                }, ignore_index=True)
        
        # Salvar como CSV
        df.to_csv(output_path, index=False, encoding='utf-8')
        return output_path
    
    def export_excel(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Exporta dados nutricionais para Excel.
        
        Args:
            data: Dados de análise nutricional
            output_path: Caminho para salvar o arquivo
        
        Returns:
            Caminho do arquivo exportado
        """
        # Similar à exportação CSV, mas usando Excel
        if 'food_details' not in data:
            raise ValueError("Dados não contêm informações de alimentos")
        
        # Criar dicionário de DataFrames para múltiplas planilhas
        with pd.ExcelWriter(output_path) as writer:
            # Planilha de detalhes dos alimentos
            rows = []
            for food_analysis in data.get('food_details', []):
                row = {
                    'food_class': food_analysis.get('food_classification', {}).get('food_class', 'Desconhecido'),
                    'confidence': food_analysis.get('food_classification', {}).get('confidence', 0),
                    'calories': food_analysis.get('nutrition', {}).get('calories', 0),
                    'proteins': food_analysis.get('nutrition', {}).get('proteins', 0),
                    'carbohydrates': food_analysis.get('nutrition', {}).get('carbohydrates', 0),
                    'fats': food_analysis.get('nutrition', {}).get('fats', 0),
                    'fiber': food_analysis.get('nutrition', {}).get('fiber', 0),
                    'vitamins': ', '.join(food_analysis.get('nutrition', {}).get('vitamins', [])),
                    'minerals': ', '.join(food_analysis.get('nutrition', {}).get('minerals', [])),
                    'health_impact': food_analysis.get('health_impact', 'Não avaliado'),
                    'food_condition': food_analysis.get('condition', {}).get('status', 'Não verificado')
                }
                rows.append(row)
            
            # DataFrame de detalhes dos alimentos
            df_details = pd.DataFrame(rows)
            df_details.to_excel(writer, sheet_name='Detalhes dos Alimentos', index=False)
            
            # Planilha de resumo nutricional
            if 'total_nutrition' in data:
                df_summary = pd.DataFrame([{
                    'Nutriente': 'Calorias',
                    'Total': data['total_nutrition'].get('calories', 0)
                }, {
                    'Nutriente': 'Proteínas',
                    'Total': data['total_nutrition'].get('proteins', 0)
                }, {
                    'Nutriente': 'Carboidratos',
                    'Total': data['total_nutrition'].get('carbohydrates', 0)
                }, {
                    'Nutriente': 'Gorduras',
                    'Total': data['total_nutrition'].get('fats', 0)
                }])
                df_summary.to_excel(writer, sheet_name='Resumo Nutricional', index=False)
            
            # Planilha de recomendações
            if 'recommendations' in data:
                df_recommendations = pd.DataFrame({
                    'Recomendações': data.get('recommendations', [])
                })
                df_recommendations.to_excel(writer, sheet_name='Recomendações', index=False)
        
        return output_path
    
    def export(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Exporta dados nutricionais em diferentes formatos.
        
        Args:
            data: Dados de análise nutricional
            output_path: Caminho para salvar o arquivo
            format: Formato de exportação (json, csv, excel)
        
        Returns:
            Caminho do arquivo exportado
        """
        # Determinar o formato baseado na extensão do arquivo de saída
        if output_path.lower().endswith('.json'):
            return self.export_json(data, output_path)
        elif output_path.lower().endswith('.csv'):
            return self.export_csv(data, output_path)
        elif output_path.lower().endswith('.xlsx') or output_path.lower().endswith('.xls'):
            return self.export_excel(data, output_path)
        else:
            # Padrão para JSON
            return self.export_json(data, output_path)

    @property
    def format_name(self) -> str:
        """Retorna o nome do formato de exportação."""
        return "nutrition"
    
    @property
    def mime_type(self) -> str:
        """Retorna o MIME type do formato de exportação."""
        return "application/json"

# O registro agora é feito através do dicionário EXPORTERS em __init__.py

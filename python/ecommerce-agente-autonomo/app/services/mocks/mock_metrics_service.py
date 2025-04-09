import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.services.interfaces import MetricsServiceInterface
from app.utils.logger import logger

class MockMetricsService(MetricsServiceInterface):
    """Serviço mock para métricas e análises."""
    
    def __init__(self):
        """Inicializa o serviço com armazenamento em memória."""
        self.interactions = []
        self.conversions = []
        self.user_metrics = {}
        self.system_metrics = {
            "day": {},
            "week": {},
            "month": {}
        }
    
    async def track_interaction(self, user_id: str, session_id: str, interaction_type: str, metadata: Dict[str, Any]) -> None:
        """Registra uma interação para análise."""
        # Cria o registro da interação
        interaction = {
            "user_id": user_id,
            "session_id": session_id,
            "type": interaction_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Adiciona à lista de interações
        self.interactions.append(interaction)
        
        # Atualiza métricas do usuário
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = {
                "interactions_count": 0,
                "last_interaction": None,
                "interaction_types": {}
            }
        
        self.user_metrics[user_id]["interactions_count"] += 1
        self.user_metrics[user_id]["last_interaction"] = interaction["timestamp"]
        
        interaction_types = self.user_metrics[user_id]["interaction_types"]
        if interaction_type not in interaction_types:
            interaction_types[interaction_type] = 0
        interaction_types[interaction_type] += 1
        
        # Atualiza métricas do sistema
        day_key = datetime.now().strftime("%Y-%m-%d")
        hour_key = datetime.now().strftime("%H")
        
        if day_key not in self.system_metrics["day"]:
            self.system_metrics["day"][day_key] = {
                "total": 0,
                "by_type": {},
                "by_hour": {}
            }
        
        self.system_metrics["day"][day_key]["total"] += 1
        
        by_type = self.system_metrics["day"][day_key]["by_type"]
        if interaction_type not in by_type:
            by_type[interaction_type] = 0
        by_type[interaction_type] += 1
        
        by_hour = self.system_metrics["day"][day_key]["by_hour"]
        if hour_key not in by_hour:
            by_hour[hour_key] = 0
        by_hour[hour_key] += 1
        
        logger.info(f"Tracked interaction: {interaction_type} for user: {user_id}")
    
    async def track_conversion(self, user_id: str, session_id: str, conversion_type: str, value: float, metadata: Dict[str, Any]) -> None:
        """Registra uma conversão (ex: adição ao carrinho, compra)."""
        # Cria o registro da conversão
        conversion = {
            "user_id": user_id,
            "session_id": session_id,
            "type": conversion_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Adiciona à lista de conversões
        self.conversions.append(conversion)
        
        # Atualiza métricas do usuário
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = {
                "conversions_count": 0,
                "total_value": 0.0,
                "conversion_types": {},
                "last_conversion": None
            }
        
        # Inicializa campos de conversão se não existirem
        if "conversions_count" not in self.user_metrics[user_id]:
            self.user_metrics[user_id]["conversions_count"] = 0
            self.user_metrics[user_id]["total_value"] = 0.0
            self.user_metrics[user_id]["conversion_types"] = {}
        
        self.user_metrics[user_id]["conversions_count"] += 1
        self.user_metrics[user_id]["total_value"] += value
        self.user_metrics[user_id]["last_conversion"] = conversion["timestamp"]
        
        conversion_types = self.user_metrics[user_id]["conversion_types"]
        if conversion_type not in conversion_types:
            conversion_types[conversion_type] = {"count": 0, "value": 0.0}
        conversion_types[conversion_type]["count"] += 1
        conversion_types[conversion_type]["value"] += value
        
        # Atualiza métricas do sistema
        day_key = datetime.now().strftime("%Y-%m-%d")
        
        if day_key not in self.system_metrics["day"]:
            self.system_metrics["day"][day_key] = {
                "conversions": {
                    "total": 0,
                    "value": 0.0,
                    "by_type": {}
                }
            }
        
        # Inicializa campos de conversão se não existirem
        if "conversions" not in self.system_metrics["day"][day_key]:
            self.system_metrics["day"][day_key]["conversions"] = {
                "total": 0,
                "value": 0.0,
                "by_type": {}
            }
        
        conversions = self.system_metrics["day"][day_key]["conversions"]
        conversions["total"] += 1
        conversions["value"] += value
        
        by_type = conversions["by_type"]
        if conversion_type not in by_type:
            by_type[conversion_type] = {"count": 0, "value": 0.0}
        by_type[conversion_type]["count"] += 1
        by_type[conversion_type]["value"] += value
        
        logger.info(f"Tracked conversion: {conversion_type} with value {value} for user: {user_id}")
    
    async def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Obtém métricas relacionadas a um usuário específico."""
        if user_id not in self.user_metrics:
            return {
                "interactions_count": 0,
                "conversions_count": 0,
                "total_value": 0.0
            }
        
        metrics = self.user_metrics[user_id].copy()
        
        # Calcula métricas derivadas
        if "conversions_count" in metrics and metrics["conversions_count"] > 0:
            metrics["average_value"] = metrics["total_value"] / metrics["conversions_count"]
        else:
            metrics["average_value"] = 0.0
        
        if "interactions_count" in metrics and "conversions_count" in metrics:
            if metrics["interactions_count"] > 0:
                metrics["conversion_rate"] = metrics["conversions_count"] / metrics["interactions_count"]
            else:
                metrics["conversion_rate"] = 0.0
        
        return metrics
    
    async def get_system_metrics(self, period: str = "day") -> Dict[str, Any]:
        """Obtém métricas gerais do sistema para um período específico."""
        if period not in ["day", "week", "month"]:
            period = "day"
        
        # Retorna as métricas do período solicitado
        metrics = self.system_metrics[period].copy()
        
        # Adiciona algumas métricas agregadas
        total_interactions = 0
        total_conversions = 0
        total_value = 0.0
        
        for day, day_metrics in metrics.items():
            if "total" in day_metrics:
                total_interactions += day_metrics["total"]
            
            if "conversions" in day_metrics:
                conversions = day_metrics["conversions"]
                if "total" in conversions:
                    total_conversions += conversions["total"]
                if "value" in conversions:
                    total_value += conversions["value"]
        
        return {
            "period": period,
            "total_interactions": total_interactions,
            "total_conversions": total_conversions,
            "total_value": total_value,
            "conversion_rate": total_conversions / total_interactions if total_interactions > 0 else 0.0,
            "average_value": total_value / total_conversions if total_conversions > 0 else 0.0,
            "detailed_metrics": metrics
        }

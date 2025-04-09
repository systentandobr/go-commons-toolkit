from typing import Dict, Any, List
import numpy as np

class VideoPostProcessor:
    """Processa resultados de análise de vídeo."""
    
    def __init__(self, task_type: str, frame_processor: Any):
        """
        Inicializa o processador de resultados de vídeo.
        
        Args:
            task_type: Tipo de tarefa ('classification', 'detection', 'segmentation')
            frame_processor: Processador para frames individuais
        """
        self.task_type = task_type
        self.frame_processor = frame_processor
        
        # Mapeamento de funções de agregação por tipo de tarefa
        self.aggregation_functions = {
            'classification': self._aggregate_classification_results,
            'detection': self._aggregate_detection_results,
            'segmentation': self._aggregate_segmentation_results,
            'video_classification': self._aggregate_classification_results
        }
    
    def process(self, outputs: List[Any]) -> Dict[str, Any]:
        """
        Processa múltiplos outputs de frames de vídeo.
        
        Args:
            outputs: Lista de outputs para cada frame do vídeo
        
        Returns:
            Resultado agregado do vídeo
        """
        # Processar cada frame individual
        frame_results = []
        for i, output in enumerate(outputs):
            frame_result = self.frame_processor.process(output)
            
            # Adicionar ID do frame ao resultado
            if isinstance(frame_result, dict):
                frame_result["frame_id"] = i
            
            frame_results.append(frame_result)
        
        # Agregar resultados conforme o tipo de tarefa
        if self.task_type in self.aggregation_functions:
            aggregated = self.aggregation_functions[self.task_type](frame_results)
        else:
            # Fallback: apenas retornar os frames sem agregação específica
            aggregated = {"frames_count": len(frame_results)}
        
        # Montagem do resultado final
        return {
            "frames": frame_results,
            "aggregated": aggregated
        }
    
    def _aggregate_classification_results(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrega resultados de classificação de múltiplos frames."""
        # Contagem de votos por classe
        class_votes = {}
        class_confidence_sum = {}
        
        for result in frame_results:
            if "predictions" in result:
                for pred in result["predictions"]:
                    class_name = pred["class_name"]
                    if class_name not in class_votes:
                        class_votes[class_name] = 0
                        class_confidence_sum[class_name] = 0.0
                    
                    class_votes[class_name] += 1
                    class_confidence_sum[class_name] += pred["confidence"]
            elif "prediction" in result:
                # Caso de classificação binária
                class_name = result["prediction"]["class_name"]
                if class_name not in class_votes:
                    class_votes[class_name] = 0
                    class_confidence_sum[class_name] = 0.0
                
                class_votes[class_name] += 1
                class_confidence_sum[class_name] += result["prediction"]["confidence"]
        
        # Calcular média de confiança para cada classe
        class_avg_confidence = {}
        for class_name, count in class_votes.items():
            class_avg_confidence[class_name] = class_confidence_sum[class_name] / count
        
        # Encontrar classe mais frequente
        if class_votes:
            top_class = max(class_votes.items(), key=lambda x: x[1])
            top_class_name = top_class[0]
            top_class_frames = top_class[1]
            top_class_confidence = class_avg_confidence[top_class_name]
        else:
            top_class_name = None
            top_class_frames = 0
            top_class_confidence = 0.0
        
        return {
            "top_class": top_class_name,
            "top_class_frames": top_class_frames,
            "top_class_confidence": float(top_class_confidence),
            "class_distribution": {name: count / len(frame_results) for name, count in class_votes.items()},
            "class_avg_confidence": class_avg_confidence
        }
    
    def _aggregate_detection_results(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrega resultados de detecção de múltiplos frames."""
        # Contagem de detecções por classe
        class_counts = {}
        # Total de detecções por frame
        detections_per_frame = []
        # Todas as detecções com ID de frame
        all_detections = []
        
        for i, frame in enumerate(frame_results):
            detections = frame.get("detections", [])
            detections_per_frame.append(len(detections))
            
            for det in detections:
                class_name = det["class_name"]
                if class_name not in class_counts:
                    class_counts[class_name] = 0
                class_counts[class_name] += 1
                
                # Adicionar ID do frame à detecção
                det_with_frame = det.copy()
                det_with_frame["frame_id"] = i
                all_detections.append(det_with_frame)
        
        # Estatísticas agregadas
        total_detections = sum(class_counts.values())
        avg_detections_per_frame = sum(detections_per_frame) / len(detections_per_frame) if detections_per_frame else 0
        
        # Calcular consistência das detecções (quantos frames têm detecções similares)
        frames_with_detections = sum(1 for count in detections_per_frame if count > 0)
        detection_consistency = frames_with_detections / len(frame_results) if frame_results else 0
        
        return {
            "class_counts": class_counts,
            "total_detections": total_detections,
            "unique_classes_detected": len(class_counts),
            "avg_detections_per_frame": float(avg_detections_per_frame),
            "max_detections_in_frame": max(detections_per_frame) if detections_per_frame else 0,
            "detection_consistency": float(detection_consistency),
            "all_detections": all_detections
        }
    
    def _aggregate_segmentation_results(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrega resultados de segmentação de múltiplos frames."""
        # Coletar todas as classes encontradas
        all_classes = set()
        for frame in frame_results:
            if "class_distribution" in frame:
                all_classes.update(frame["class_distribution"].keys())
        
        # Calcular distribuição média de classes por frame
        avg_class_distribution = {cls: 0.0 for cls in all_classes}
        for frame in frame_results:
            if "class_distribution" in frame:
                for cls, percentage in frame["class_distribution"].items():
                    avg_class_distribution[cls] += percentage / len(frame_results)
        
        # Encontrar classe dominante média
        dominant_class = max(avg_class_distribution.items(), key=lambda x: x[1])[0] if avg_class_distribution else None
        
        # Contar frames onde cada classe é dominante
        dominant_class_counts = {}
        for frame in frame_results:
            if "dominant_class" in frame and frame["dominant_class"]:
                dominant = frame["dominant_class"]
                if dominant not in dominant_class_counts:
                    dominant_class_counts[dominant] = 0
                dominant_class_counts[dominant] += 1
        
        # Classe dominante por contagem de frames
        frame_dominant_class = max(dominant_class_counts.items(), key=lambda x: x[1])[0] if dominant_class_counts else None
        
        return {
            "average_class_distribution": avg_class_distribution,
            "per_frame_dominant_class": dominant_class_counts,
            "frame_dominant_class": frame_dominant_class,
            "area_dominant_class": dominant_class
        }

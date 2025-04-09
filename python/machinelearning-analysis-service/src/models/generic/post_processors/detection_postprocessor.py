from typing import Dict, Any, List, Optional
import tensorflow as tf
import numpy as np

class DetectionPostProcessor:
    """Processa resultados de modelos de detecção de objetos."""
    
    def __init__(self, 
                 class_labels: List[str], 
                 output_format: str = 'default',
                 confidence_threshold: float = 0.5,
                 apply_nms: bool = True,
                 iou_threshold: float = 0.5,
                 max_detections: int = 100):
        """
        Inicializa o processador.
        
        Args:
            class_labels: Lista com nomes das classes
            output_format: Formato de saída do modelo ('default', 'yolo', 'ssd', 'faster_rcnn')
            confidence_threshold: Limiar de confiança para filtrar detecções
            apply_nms: Se True, aplica Non-Maximum Suppression
            iou_threshold: Limiar IoU para NMS
            max_detections: Número máximo de detecções a retornar
        """
        self.class_labels = class_labels
        self.output_format = output_format
        self.confidence_threshold = confidence_threshold
        self.apply_nms = apply_nms
        self.iou_threshold = iou_threshold
        self.max_detections = max_detections
        
        # Mapeamento de função de processamento por formato
        self.format_processors = {
            'default': self._process_default,
            'yolo': self._process_yolo,
            'ssd': self._process_ssd,
            'faster_rcnn': self._process_faster_rcnn
        }
    
    def process(self, output: Any) -> Dict[str, Any]:
        """Processa resultado de detecção conforme o formato configurado."""
        # Verificar se temos uma função de processamento para o formato
        if self.output_format in self.format_processors:
            return self.format_processors[self.output_format](output)
        else:
            # Fallback para processador padrão
            return self._process_default(output)
    
    def _process_default(self, output: Any) -> Dict[str, Any]:
        """Processa formato padrão [batch, num_detections, 4 + num_classes]."""
        # Converter para numpy se for tensor TF
        if hasattr(output, 'numpy'):
            output_np = output.numpy()
        else:
            output_np = np.array(output)
        
        # Extrair boxes, scores e classes
        boxes = output_np[0, :, :4]
        scores = np.max(output_np[0, :, 4:], axis=1)
        class_indices = np.argmax(output_np[0, :, 4:], axis=1)
        
        # Filtrar por confiança
        valid_indices = scores > self.confidence_threshold
        
        filtered_boxes = boxes[valid_indices]
        filtered_scores = scores[valid_indices]
        filtered_classes = class_indices[valid_indices]
        
        # Aplicar NMS se configurado
        if self.apply_nms and len(filtered_boxes) > 0:
            from tensorflow.image import non_max_suppression
            
            selected_indices = non_max_suppression(
                filtered_boxes,
                filtered_scores,
                max_output_size=self.max_detections,
                iou_threshold=self.iou_threshold
            ).numpy()
            
            filtered_boxes = filtered_boxes[selected_indices]
            filtered_scores = filtered_scores[selected_indices]
            filtered_classes = filtered_classes[selected_indices]
        
        # Formatar resultados
        detections = []
        for i in range(len(filtered_boxes)):
            class_id = int(filtered_classes[i])
            class_name = self.class_labels[class_id] if class_id < len(self.class_labels) else f"class_{class_id}"
            
            detection = {
                "box": filtered_boxes[i].tolist(),  # [y1, x1, y2, x2]
                "score": float(filtered_scores[i]),
                "class_id": class_id,
                "class_name": class_name
            }
            detections.append(detection)
        
        return {
            "detections": detections,
            "count": len(detections)
        }
    
    def _process_yolo(self, output: Any) -> Dict[str, Any]:
        """Processa saída no formato YOLO."""
        # Implementação simplificada para YOLO
        # Na prática, precisaria ser adaptada para a versão específica do YOLO
        # Retorna um resultado vazio por enquanto
        return {"detections": [], "count": 0}
    
    def _process_ssd(self, output: Any) -> Dict[str, Any]:
        """Processa saída no formato SSD."""
        # Formato típico SSD: [boxes, scores, classes, num_detections]
        boxes = output[0]
        scores = output[1]
        classes = output[2]
        num_detections = int(output[3][0])
        
        # Filtrar por confiança
        valid_indices = np.where(scores[0, :num_detections] > self.confidence_threshold)[0]
        
        detections = []
        for i in valid_indices:
            class_id = int(classes[0, i])
            class_name = self.class_labels[class_id] if class_id < len(self.class_labels) else f"class_{class_id}"
            
            detection = {
                "box": boxes[0, i].tolist(),
                "score": float(scores[0, i]),
                "class_id": class_id,
                "class_name": class_name
            }
            detections.append(detection)
        
        return {
            "detections": detections,
            "count": len(detections)
        }
    
    def _process_faster_rcnn(self, output: Any) -> Dict[str, Any]:
        """Processa saída no formato Faster R-CNN."""
        # Formato típico de dicionário do Faster R-CNN
        boxes = output["detection_boxes"]
        scores = output["detection_scores"]
        classes = output["detection_classes"]
        num_detections = int(output["num_detections"])
        
        # Filtrar por confiança
        valid_indices = np.where(scores[:num_detections] > self.confidence_threshold)[0]
        
        detections = []
        for i in valid_indices:
            class_id = int(classes[i])
            class_name = self.class_labels[class_id] if class_id < len(self.class_labels) else f"class_{class_id}"
            
            detection = {
                "box": boxes[i].tolist(),
                "score": float(scores[i]),
                "class_id": class_id,
                "class_name": class_name
            }
            detections.append(detection)
        
        return {
            "detections": detections,
            "count": len(detections)
        }

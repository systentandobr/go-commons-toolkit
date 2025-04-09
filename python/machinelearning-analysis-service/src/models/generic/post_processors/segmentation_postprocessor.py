from typing import Dict, Any, List
import tensorflow as tf
import numpy as np

class SegmentationPostProcessor:
    """Processa resultados de modelos de segmentação semântica."""
    
    def __init__(self, class_labels: List[str]):
        """
        Inicializa o processador.
        
        Args:
            class_labels: Lista com nomes das classes
        """
        self.class_labels = class_labels
    
    def process(self, output: Any) -> Dict[str, Any]:
        """Processa resultado de segmentação."""
        # Converter para numpy se for tensor TF
        if hasattr(output, 'numpy'):
            output_np = output.numpy()
        else:
            output_np = np.array(output)
        
        # Verificar formato da saída
        # Formato [batch, height, width, num_classes]
        if len(output_np.shape) == 4 and output_np.shape[-1] > 1:
            # Saída one-hot ou probabilidades por classe
            seg_map = np.argmax(output_np[0], axis=-1)
        else:
            # Mapa de segmentação já processado
            seg_map = output_np[0]
        
        # Contar áreas por classe
        unique_classes, class_counts = np.unique(seg_map, return_counts=True)
        
        # Calcular porcentagens por classe
        total_pixels = seg_map.size
        class_percentages = {}
        for i, class_id in enumerate(unique_classes):
            class_name = self.class_labels[class_id] if class_id < len(self.class_labels) else f"class_{class_id}"
            percentage = (class_counts[i] / total_pixels) * 100
            class_percentages[class_name] = float(percentage)
        
        # Encontrar classe dominante
        dominant_class = max(class_percentages.items(), key=lambda x: x[1])[0] if class_percentages else None
        
        # Versão comprimida do mapa para transmissão
        # Por simplicidade, apenas convertemos para RLE (Run-Length Encoding) básico
        encoded_map = self._simple_rle_encode(seg_map)
        
        return {
            "segmentation_map_encoded": encoded_map,
            "shape": seg_map.shape,
            "class_distribution": class_percentages,
            "dominant_class": dominant_class,
            "unique_classes": [int(c) for c in unique_classes.tolist()],
            "class_names": [self.class_labels[c] if c < len(self.class_labels) else f"class_{c}" 
                          for c in unique_classes]
        }
    
    def _simple_rle_encode(self, mask: np.ndarray) -> List[Dict[str, Any]]:
        """
        Implementa uma versão simplificada de Run-Length Encoding.
        
        Args:
            mask: Mapa de segmentação [height, width]
            
        Returns:
            Lista com segmentos codificados
        """
        # Garantir que é 2D
        flat_mask = mask.flatten()
        
        segments = []
        current_value = flat_mask[0]
        start_idx = 0
        
        for i in range(1, len(flat_mask)):
            if flat_mask[i] != current_value:
                segments.append({
                    "value": int(current_value),
                    "start": start_idx,
                    "length": i - start_idx
                })
                current_value = flat_mask[i]
                start_idx = i
        
        # Adicionar o último segmento
        segments.append({
            "value": int(current_value),
            "start": start_idx,
            "length": len(flat_mask) - start_idx
        })
        
        return segments

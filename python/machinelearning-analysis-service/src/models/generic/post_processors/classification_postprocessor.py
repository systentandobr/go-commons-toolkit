from typing import Dict, Any, List
import tensorflow as tf
import numpy as np

class ClassificationPostProcessor:
    """Processa resultados de modelos de classificação."""
    
    def __init__(self, class_labels: List[str], top_k: int = 5):
        """
        Inicializa o processador.
        
        Args:
            class_labels: Lista com nomes das classes
            top_k: Número de classes top a retornar
        """
        self.class_labels = class_labels
        self.top_k = top_k
    
    def process(self, output: tf.Tensor) -> Dict[str, Any]:
        """Processa resultado de classificação."""
        # Garantir que temos o formato adequado
        if hasattr(output, 'numpy'):
            output_np = output.numpy()
        else:
            output_np = np.array(output)
            
        # Verificar se precisamos aplicar softmax
        if self.should_apply_softmax(output_np):
            probs = tf.nn.softmax(output, axis=-1).numpy()
        else:
            probs = output_np
        
        # Se for modelo multi-classe
        if probs.shape[1] > 1:
            return self._process_multiclass(probs)
        else:  # Modelo binário
            return self._process_binary(probs)
    
    def should_apply_softmax(self, output: np.ndarray) -> bool:
        """Verifica se é necessário aplicar softmax."""
        # Se já for probabilidades (soma próxima a 1)
        if output.shape[1] > 1:
            row_sums = np.sum(output, axis=1)
            return not np.allclose(row_sums, 1.0, atol=1e-5)
        return True  # Por padrão aplicamos softmax em saídas raw
    
    def _process_multiclass(self, probs: np.ndarray) -> Dict[str, Any]:
        """Processa classificação multi-classe."""
        # Garantir que não excedemos o número de classes
        actual_k = min(self.top_k, probs.shape[1])
        
        # Encontrar os top-k índices
        indices = np.argsort(probs[0])[-actual_k:][::-1]
        
        predictions = []
        for i in indices:
            label = self.class_labels[i] if i < len(self.class_labels) else f"class_{i}"
            predictions.append({
                "class_id": int(i),
                "class_name": label,
                "confidence": float(probs[0][i])
            })
            
        return {
            "predictions": predictions,
            "top_class": predictions[0]["class_name"],
            "top_confidence": predictions[0]["confidence"]
        }
    
    def _process_binary(self, probs: np.ndarray) -> Dict[str, Any]:
        """Processa classificação binária."""
        if probs.shape[1] == 1:
            # Formato [batch, 1]
            confidence = float(probs[0][0])
            is_positive = confidence >= 0.5
        else:
            # Formato [batch, 2] (background, foreground)
            confidence = float(probs[0][1])
            is_positive = confidence >= 0.5
        
        # Garantir que temos pelo menos 2 labels
        if len(self.class_labels) < 2:
            self.class_labels = ["negative", "positive"]
            
        class_id = 1 if is_positive else 0
        class_name = self.class_labels[class_id]
        
        prediction = {
            "class_id": class_id,
            "class_name": class_name,
            "confidence": confidence if is_positive else 1.0 - confidence
        }
            
        return {
            "prediction": prediction,
            "is_positive": is_positive
        }

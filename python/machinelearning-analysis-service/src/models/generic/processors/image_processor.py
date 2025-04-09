from typing import Any, List, Tuple, Optional
import tensorflow as tf
import numpy as np


class ImageProcessor:
    """Classe responsável pelo processamento de imagens."""
    
    def __init__(self, 
                 target_size: Tuple[int, int],
                 normalize: bool = True,
                 mean: Optional[List[float]] = None,
                 std: Optional[List[float]] = None,
                 add_batch_dim: bool = True):
        """
        Inicializa o processador de imagens.
        
        Args:
            target_size: Tamanho alvo para redimensionamento (altura, largura)
            normalize: Se True, normaliza os valores dos pixels
            mean: Valores médios por canal para normalização
            std: Valores de desvio padrão por canal para normalização
            add_batch_dim: Se True, adiciona dimensão de batch
        """
        self.target_size = target_size
        self.normalize = normalize
        self.mean = mean
        self.std = std
        self.add_batch_dim = add_batch_dim
    
    def process_from_path(self, path: str) -> tf.Tensor:
        """Processa imagem a partir do caminho do arquivo."""
        img = tf.io.read_file(path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        return self.standardize_image(img)
    
    def process_from_bytes(self, data: bytes) -> tf.Tensor:
        """Processa imagem a partir de dados binários."""
        img = tf.image.decode_image(tf.constant(data), channels=3, expand_animations=False)
        return self.standardize_image(img)
    
    def process_from_array(self, array: np.ndarray) -> tf.Tensor:
        """Processa imagem a partir de array NumPy."""
        img = tf.convert_to_tensor(array)
        return self.standardize_image(img)
    
    def standardize_image(self, img: tf.Tensor) -> tf.Tensor:
        """Padroniza imagem para o formato esperado pelo modelo."""
        # Garantir que a imagem é float32
        if img.dtype != tf.float32:
            img = tf.cast(img, tf.float32)
            
        # Redimensionar
        img = tf.image.resize(img, self.target_size)
        
        # Normalizar
        if self.normalize:
            img = img / 255.0
            
            # Aplicar normalização específica se configurada
            if self.mean is not None and self.std is not None:
                img = (img - self.mean) / self.std
        
        # Adicionar dimensão de batch se necessário
        if self.add_batch_dim and len(img.shape) == 3:
            img = tf.expand_dims(img, 0)
            
        return img

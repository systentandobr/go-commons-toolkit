from typing import List, Any
import tensorflow as tf

class VideoProcessor:
    """Classe responsável pelo processamento de vídeos."""
    
    def __init__(self, image_processor, max_frames: int = 30, frame_interval: int = 1):
        """
        Inicializa o processador de vídeos.
        
        Args:
            image_processor: Instância de ImageProcessor para processar frames individuais
            max_frames: Número máximo de frames a processar
            frame_interval: Intervalo entre frames a capturar
        """
        self.image_processor = image_processor
        self.max_frames = max_frames
        self.frame_interval = frame_interval
    
    def process_video(self, path: str) -> List[tf.Tensor]:
        """Processa vídeo extraindo e padronizando frames."""
        try:
            import cv2
        except ImportError:
            raise ImportError("OpenCV (cv2) é necessário para processamento de vídeo. Instale com 'pip install opencv-python'")
            
        cap = cv2.VideoCapture(path)
        frames = []
        
        frame_count = 0
        while cap.isOpened() and len(frames) < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % self.frame_interval == 0:
                # Converter BGR para RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Processar frame como imagem
                frame_tensor = self.image_processor.standardize_image(tf.convert_to_tensor(frame))
                frames.append(frame_tensor)
                
            frame_count += 1
            
        cap.release()
        
        # Adicionar metadados do vídeo
        self.metadata = {
            "total_frames": frame_count,
            "processed_frames": len(frames),
            "frame_interval": self.frame_interval,
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }
        
        return frames

import tensorflow as tf
from typing import Any, Dict
from .protocols import ExecutionContextProtocol

class TensorFlowContext(ExecutionContextProtocol):
    """Contexto de execução para modelos TensorFlow."""
    
    def __init__(self, gpu_enabled: bool = True, memory_limit: int = None, mixed_precision: bool = False):
        """Inicializa o contexto TensorFlow.
        
        Args:
            gpu_enabled: Se True, utiliza GPU quando disponível
            memory_limit: Limite de memória em MB para GPU (None = sem limite)
            mixed_precision: Se True, utiliza precisão mista para aceleração
        """
        self.gpu_enabled = gpu_enabled
        self.memory_limit = memory_limit
        self.mixed_precision = mixed_precision
        
        # Configuração para uso de GPU se disponível e habilitado
        if not gpu_enabled:
            tf.config.set_visible_devices([], 'GPU')
        elif memory_limit:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)
                        tf.config.set_logical_device_configuration(
                            gpu,
                            [tf.config.LogicalDeviceConfiguration(memory_limit=memory_limit)]
                        )
                except RuntimeError as e:
                    print(f"GPU configuration error: {e}")
        
        # Configurar precisão mista se solicitado
        if mixed_precision:
            tf.keras.mixed_precision.set_global_policy('mixed_float16')
    
    def load_model(self, model_path: str) -> tf.keras.Model:
        """Carrega um modelo TensorFlow salvo."""
        try:
            # Tenta carregar como SavedModel
            return tf.keras.models.load_model(model_path)
        except (ImportError, IOError) as e:
            # Tenta carregar como arquivo H5
            if model_path.endswith('.h5'):
                return tf.keras.models.load_model(model_path)
            else:
                try:
                    return tf.keras.models.load_model(f"{model_path}.h5")
                except:
                    raise ValueError(f"Não foi possível carregar o modelo: {str(e)}")
    
    def run_inference(self, model: tf.keras.Model, inputs: Any) -> Any:
        """Executa inferência usando o modelo TensorFlow."""
        return model(inputs, training=False)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o contexto TensorFlow."""
        return {
            "context_type": "tensorflow",
            "version": tf.__version__,
            "gpu_enabled": self.gpu_enabled,
            "gpu_available": len(tf.config.list_physical_devices('GPU')) > 0,
            "devices": [d.name for d in tf.config.list_physical_devices()],
            "mixed_precision": self.mixed_precision,
            "memory_limit": self.memory_limit
        }


class ONNXContext(ExecutionContextProtocol):
    """Contexto de execução para modelos ONNX."""
    
    def __init__(self, providers=None):
        """Inicializa o contexto ONNX.
        
        Args:
            providers: Lista de providers ONNX (None = usa padrões disponíveis)
        """
        self.providers = providers
        
        # Importação tardia para não exigir dependência se não for usado
        try:
            import onnxruntime as ort
            self._ort = ort
            
            if providers is None:
                available_providers = ort.get_available_providers()
                # Prioriza execução em GPU se disponível
                if 'CUDAExecutionProvider' in available_providers:
                    self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                else:
                    self.providers = ['CPUExecutionProvider']
            
            self._session = None
        except ImportError:
            raise ImportError("ONNX Runtime não está instalado. Instale com 'pip install onnxruntime-gpu' ou 'pip install onnxruntime'")
    
    def load_model(self, model_path: str) -> Any:
        """Carrega um modelo ONNX."""
        self._session = self._ort.InferenceSession(model_path, providers=self.providers)
        return self._session
    
    def run_inference(self, model: Any, inputs: Any) -> Any:
        """Executa inferência usando o modelo ONNX."""
        # Determinar nomes de entrada e saída do modelo
        input_name = model.get_inputs()[0].name
        output_names = [output.name for output in model.get_outputs()]
        
        # Preparar entrada
        if isinstance(inputs, dict):
            # Entrada já está no formato de dicionário
            input_dict = inputs
        else:
            # Convertemos para o formato esperado pelo ONNX
            input_dict = {input_name: inputs}
        
        # Executar inferência
        outputs = model.run(output_names, input_dict)
        
        # Se tivermos apenas uma saída, retorna diretamente
        if len(outputs) == 1:
            return outputs[0]
        return outputs
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o contexto ONNX."""
        return {
            "context_type": "onnx",
            "version": self._ort.__version__,
            "providers": self.providers,
            "available_providers": self._ort.get_available_providers()
        }


class PyTorchContext(ExecutionContextProtocol):
    """Contexto de execução para modelos PyTorch."""
    
    def __init__(self, gpu_enabled: bool = True, device_id: int = 0):
        """Inicializa o contexto PyTorch.
        
        Args:
            gpu_enabled: Se True, utiliza GPU quando disponível
            device_id: ID do dispositivo GPU a ser usado
        """
        # Importação tardia para não exigir dependência se não for usado
        try:
            import torch
            self._torch = torch
            
            self.gpu_enabled = gpu_enabled
            self.device_id = device_id
            
            if gpu_enabled and torch.cuda.is_available():
                self.device = torch.device(f"cuda:{device_id}")
            else:
                self.device = torch.device("cpu")
                
        except ImportError:
            raise ImportError("PyTorch não está instalado. Instale com 'pip install torch'")
    
    def load_model(self, model_path: str) -> Any:
        """Carrega um modelo PyTorch."""
        model = self._torch.load(model_path, map_location=self.device)
        
        # Verificar se é um estado de modelo ou um modelo completo
        if isinstance(model, dict) and 'state_dict' in model:
            # Precisamos de uma definição de modelo, não apenas o estado
            raise ValueError("O arquivo contém apenas o state_dict. Forneça uma definição de modelo completa.")
        
        # Coloca o modelo no modo de avaliação
        model.eval()
        return model
    
    def run_inference(self, model: Any, inputs: Any) -> Any:
        """Executa inferência usando o modelo PyTorch."""
        with self._torch.no_grad():
            # Converter entrada para tensor PyTorch se necessário
            if not isinstance(inputs, self._torch.Tensor):
                if isinstance(inputs, (list, tuple)):
                    inputs = [self._ensure_tensor(x).to(self.device) for x in inputs]
                else:
                    inputs = self._ensure_tensor(inputs).to(self.device)
            
            # Executa inferência
            outputs = model(inputs)
            
            # Converter saída para CPU/numpy para compatibilidade
            if isinstance(outputs, self._torch.Tensor):
                return outputs.cpu().numpy()
            elif isinstance(outputs, (list, tuple)) and all(isinstance(x, self._torch.Tensor) for x in outputs):
                return [x.cpu().numpy() for x in outputs]
            else:
                return outputs
    
    def _ensure_tensor(self, data: Any) -> Any:
        """Converte dados para tensor PyTorch se necessário."""
        if isinstance(data, self._torch.Tensor):
            return data
        elif isinstance(data, (list, tuple)):
            return self._torch.tensor(data)
        elif isinstance(data, np.ndarray):
            return self._torch.from_numpy(data)
        else:
            return self._torch.tensor(data)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadados sobre o contexto PyTorch."""
        return {
            "context_type": "pytorch",
            "version": self._torch.__version__,
            "gpu_enabled": self.gpu_enabled,
            "gpu_available": self._torch.cuda.is_available(),
            "device": str(self.device),
            "device_count": self._torch.cuda.device_count() if self._torch.cuda.is_available() else 0
        }

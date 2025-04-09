{
  `path`: `/home/marcelio/developing/systentando/toolkit-dev/python/machinelearning-analysis-service/GUIDE.md`,
  `content`: `# Machine Learning Analysis Service - Guia de Implementação

## Visão Geral

O `machinelearning-analysis-service` é um serviço modular e extensível para análise de imagens, vídeos e outros tipos de dados usando TensorFlow e técnicas avançadas de machine learning. O serviço implementa o padrão `@modelcontextprotocol` para facilitar a criação, carregamento e utilização de diferentes modelos de forma padronizada.

## Conceitos Principais

### ModelContextProtocol

O padrão `@modelcontextprotocol` é uma abordagem de design que permite desacoplar:
1. **Modelos de Machine Learning** - Os algoritmos e pesos treinados
2. **Contextos de Execução** - Ambientes onde os modelos são executados
3. **Protocolos de Interface** - Contratos padronizados de entrada/saída

Isso traz vários benefícios:
- **Intercambialidade** - Trocar modelos sem alterar o código do consumidor
- **Versionamento** - Gerenciar múltiplas versões de modelos de forma consistente
- **Extensibilidade** - Adicionar novos tipos de análise preservando interfaces
- **Testabilidade** - Testar de forma isolada cada camada do sistema

## Arquitetura

```
machinelearning-analysis-service/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── protocols.py      # Definições de protocolos e interfaces
│   │   ├── context.py        # Implementações de contextos de execução
│   │   └── registry.py       # Registro de modelos disponíveis
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # Classes base para modelos
│   │   ├── image/            # Modelos específicos para imagens
│   │   ├── video/            # Modelos específicos para vídeos
│   │   └── custom/           # Espaço para modelos personalizados
│   │
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── preprocessing/    # Transformações de entrada
│   │   ├── inference/        # Execução de inferência
│   │   └── postprocessing/   # Transformações de saída
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/           # Endpoints da API
│   │   ├── middlewares/      # Middlewares para autenticação, logs, etc
│   │   └── dependencies.py   # Dependências da API
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── requests.py       # Esquemas para requisições
│   │   ├── responses.py      # Esquemas para respostas
│   │   └── models.py         # Esquemas para modelos de dados
│   │
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── json_exporter.py  # Exportador de resultados em JSON
│   │   ├── csv_exporter.py   # Exportador de resultados em CSV
│   │   └── parquet_exporter.py # Exportador de resultados em Parquet
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py        # Configuração de logs
│       ├── metrics.py        # Coletores de métricas
│       └── storage.py        # Abstração para armazenamento
│
├── tests/
│   ├── unit/                 # Testes unitários
│   └── integration/          # Testes de integração
│
├── models_repository/        # Repositório local de modelos salvos
│
├── config/
│   ├── settings.py           # Configurações do serviço
│   └── logging.yaml          # Configuração de logs
│
├── scripts/
│   ├── download_models.py    # Script para baixar modelos pré-treinados
│   └── benchmark.py          # Script para benchmarking de modelos
│
├── pyproject.toml            # Configuração do projeto e dependências
├── README.md                 # Documentação geral
└── Dockerfile                # Definição de container
```

## Como Implementar Usando `@modelcontextprotocol`

### 1. Defina os Protocolos

```python
# src/core/protocols.py
from typing import Protocol, TypeVar, Any, Dict, List
import numpy as np

T = TypeVar('T')
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class ModelProtocol(Protocol[InputType, OutputType]):
    \"\"\"Protocolo para modelos de machine learning.\"\"\"
    
    model_id: str
    version: str
    
    def preprocess(self, inputs: Any) -> InputType:
        \"\"\"Prepara os dados para inferência.\"\"\"
        ...
    
    def predict(self, inputs: InputType) -> OutputType:
        \"\"\"Executa a predição no modelo.\"\"\"
        ...
    
    def postprocess(self, outputs: OutputType) -> Dict[str, Any]:
        \"\"\"Processa resultados da inferência para formato final.\"\"\"
        ...

class ExecutionContextProtocol(Protocol):
    \"\"\"Protocolo para contextos de execução.\"\"\"
    
    def load_model(self, model_path: str) -> Any:
        \"\"\"Carrega um modelo a partir do caminho especificado.\"\"\"
        ...
    
    def run_inference(self, model: Any, inputs: Any) -> Any:
        \"\"\"Executa inferência usando o modelo fornecido.\"\"\"
        ...
    
    def get_metadata(self) -> Dict[str, Any]:
        \"\"\"Retorna metadados sobre o contexto de execução.\"\"\"
        ...

class ModelContextProtocol(Protocol):
    \"\"\"Protocolo combinado que representa um modelo em um contexto de execução.\"\"\"
    
    model: ModelProtocol
    context: ExecutionContextProtocol
    
    def analyze(self, inputs: Any) -> Dict[str, Any]:
        \"\"\"Executa a análise completa incluindo pré, inferência e pós-processamento.\"\"\"
        ...
    
    def get_info(self) -> Dict[str, Any]:
        \"\"\"Retorna informações sobre o modelo e contexto.\"\"\"
        ...
```

### 2. Implemente os Contextos de Execução

```python
# src/core/context.py
import tensorflow as tf
from typing import Any, Dict
from .protocols import ExecutionContextProtocol

class TensorFlowContext(ExecutionContextProtocol):
    \"\"\"Contexto de execução para modelos TensorFlow.\"\"\"
    
    def __init__(self, gpu_enabled: bool = True):
        \"\"\"Inicializa o contexto TensorFlow.\"\"\"
        self.gpu_enabled = gpu_enabled
        
        # Configuração para uso de GPU se disponível e habilitado
        if not gpu_enabled:
            tf.config.set_visible_devices([], 'GPU')
    
    def load_model(self, model_path: str) -> tf.keras.Model:
        \"\"\"Carrega um modelo TensorFlow salvo.\"\"\"
        return tf.keras.models.load_model(model_path)
    
    def run_inference(self, model: tf.keras.Model, inputs: Any) -> Any:
        \"\"\"Executa inferência usando o modelo TensorFlow.\"\"\"
        return model(inputs, training=False)
    
    def get_metadata(self) -> Dict[str, Any]:
        \"\"\"Retorna metadados sobre o contexto TensorFlow.\"\"\"
        return {
            \"context_type\": \"tensorflow\",
            \"version\": tf.__version__,
            \"gpu_enabled\": self.gpu_enabled,
            \"gpu_available\": len(tf.config.list_physical_devices('GPU')) > 0,
            \"devices\": [d.name for d in tf.config.list_physical_devices()]
        }
```

### 3. Implemente Modelos Base

```python
# src/models/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
import os
import numpy as np
from ..core.protocols import ModelProtocol, ExecutionContextProtocol

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')

class BaseModel(ModelProtocol, Generic[InputType, OutputType], ABC):
    \"\"\"Classe base para todos os modelos de ML.\"\"\"
    
    def __init__(self, model_id: str, version: str):
        self.model_id = model_id
        self.version = version
        self._model = None
    
    @abstractmethod
    def preprocess(self, inputs: Any) -> InputType:
        \"\"\"Implementado pelas subclasses.\"\"\"
        pass
    
    @abstractmethod
    def predict(self, inputs: InputType) -> OutputType:
        \"\"\"Implementado pelas subclasses.\"\"\"
        pass
    
    @abstractmethod
    def postprocess(self, outputs: OutputType) -> Dict[str, Any]:
        \"\"\"Implementado pelas subclasses.\"\"\"
        pass

class ModelContext:
    \"\"\"Combina um modelo com um contexto de execução.\"\"\"
    
    def __init__(self, model: ModelProtocol, context: ExecutionContextProtocol):
        self.model = model
        self.context = context
    
    def analyze(self, inputs: Any) -> Dict[str, Any]:
        \"\"\"Executa o pipeline completo de análise.\"\"\"
        # Pré-processamento
        processed_inputs = self.model.preprocess(inputs)
        
        # Inferência
        raw_outputs = self.model.predict(processed_inputs)
        
        # Pós-processamento
        results = self.model.postprocess(raw_outputs)
        
        # Adicionar metadados
        results[\"metadata\"] = {
            \"model_id\": self.model.model_id,
            \"model_version\": self.model.version,
            \"context\": self.context.get_metadata()
        }
        
        return results
    
    def get_info(self) -> Dict[str, Any]:
        \"\"\"Retorna informações sobre o modelo e contexto.\"\"\"
        return {
            \"model\": {
                \"id\": self.model.model_id,
                \"version\": self.model.version
            },
            \"context\": self.context.get_metadata()
        }
```

### 4. Implemente um Modelo de Exemplo

```python
# src/models/image/object_detection.py
from typing import Any, Dict, List
import numpy as np
import tensorflow as tf
from ...core.protocols import InputType, OutputType
from ..base import BaseModel

class ObjectDetectionModel(BaseModel[tf.Tensor, tf.Tensor]):
    \"\"\"Modelo para detecção de objetos em imagens.\"\"\"
    
    def __init__(self, model_id: str, version: str, model_path: str, labels_path: str):
        super().__init__(model_id, version)
        self.model_path = model_path
        self.labels_path = labels_path
        self._model = None
        self._labels = None
        
    def _load(self, context):
        \"\"\"Carrega o modelo e labels usando o contexto fornecido.\"\"\"
        if self._model is None:
            self._model = context.load_model(self.model_path)
            
        if self._labels is None:
            with open(self.labels_path, 'r') as f:
                self._labels = [line.strip() for line in f.readlines()]
    
    def preprocess(self, inputs: Any) -> tf.Tensor:
        \"\"\"Pré-processa a imagem para o formato esperado pelo modelo.\"\"\"
        # Assumindo que inputs é um caminho para uma imagem ou um array de bytes
        if isinstance(inputs, str):
            # Carrega imagem do caminho
            img = tf.io.read_file(inputs)
            img = tf.image.decode_image(img, channels=3)
        elif isinstance(inputs, bytes):
            # Carrega imagem de bytes
            img = tf.image.decode_image(tf.constant(inputs), channels=3)
        elif isinstance(inputs, np.ndarray):
            # Já é um array NumPy
            img = tf.convert_to_tensor(inputs)
        else:
            raise ValueError(f\"Tipo de entrada não suportado: {type(inputs)}\")
        
        # Redimensiona para o tamanho esperado pelo modelo
        img = tf.image.resize(img, (224, 224))
        
        # Normaliza
        img = img / 255.0
        
        # Adiciona dimensão de batch
        img = tf.expand_dims(img, 0)
        
        return img
    
    def predict(self, inputs: tf.Tensor) -> tf.Tensor:
        \"\"\"Executa a inferência no modelo.\"\"\"
        if self._model is None:
            raise ValueError(\"Modelo não carregado. Use load_model com um contexto antes.\")
        
        return self._model(inputs)
    
    def postprocess(self, outputs: tf.Tensor) -> Dict[str, Any]:
        \"\"\"Processa as saídas do modelo para um formato amigável.\"\"\"
        # Assumindo saídas no formato [batch, num_boxes, 4 + num_classes]
        # Onde 4 representa [y1, x1, y2, x2] e o restante são as probabilidades de classe
        
        # Extrair boxes, scores e classes
        boxes = outputs[0, :, :4].numpy()
        scores = np.max(outputs[0, :, 4:], axis=1)
        class_indices = np.argmax(outputs[0, :, 4:], axis=1)
        
        # Filtrar por confiança
        threshold = 0.5
        valid_indices = scores > threshold
        
        filtered_boxes = boxes[valid_indices]
        filtered_scores = scores[valid_indices]
        filtered_classes = class_indices[valid_indices]
        
        # Formatar resultados
        detections = []
        for i in range(len(filtered_boxes)):
            detection = {
                \"box\": filtered_boxes[i].tolist(),  # [y1, x1, y2, x2]
                \"score\": float(filtered_scores[i]),
                \"class_id\": int(filtered_classes[i]),
                \"class_name\": self._labels[filtered_classes[i]] if self._labels else str(filtered_classes[i])
            }
            detections.append(detection)
        
        return {
            \"detections\": detections,
            \"count\": len(detections)
        }
```

### 5. Registre e Gerencie Modelos

```python
# src/core/registry.py
from typing import Dict, List, Any, Optional, Type
from .protocols import ModelProtocol, ExecutionContextProtocol
from ..models.base import ModelContext

class ModelRegistry:
    \"\"\"Registro global de modelos disponíveis.\"\"\"
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._models = {}
            cls._instance._contexts = {}
        return cls._instance
    
    def register_model(self, model: ModelProtocol) -> None:
        \"\"\"Registra um modelo no registro.\"\"\"
        model_key = f\"{model.model_id}@{model.version}\"
        self._models[model_key] = model
    
    def register_context(self, name: str, context: ExecutionContextProtocol) -> None:
        \"\"\"Registra um contexto de execução no registro.\"\"\"
        self._contexts[name] = context
    
    def get_model(self, model_id: str, version: str = \"latest\") -> Optional[ModelProtocol]:
        \"\"\"Obtém um modelo pelo ID e versão.\"\"\"
        model_key = f\"{model_id}@{version}\"
        return self._models.get(model_key)
    
    def get_context(self, name: str) -> Optional[ExecutionContextProtocol]:
        \"\"\"Obtém um contexto de execução pelo nome.\"\"\"
        return self._contexts.get(name)
    
    def create_model_context(
        self, model_id: str, version: str = \"latest\", context_name: str = \"default\"
    ) -> Optional[ModelContext]:
        \"\"\"Cria um ModelContext combinando um modelo e um contexto.\"\"\"
        model = self.get_model(model_id, version)
        context = self.get_context(context_name)
        
        if model is None or context is None:
            return None
        
        return ModelContext(model, context)
    
    def list_available_models(self) -> List[Dict[str, str]]:
        \"\"\"Lista todos os modelos disponíveis no registro.\"\"\"
        models = []
        for model_key in self._models:
            model_id, version = model_key.split('@')
            models.append({\"id\": model_id, \"version\": version})
        return models
    
    def list_available_contexts(self) -> List[str]:
        \"\"\"Lista todos os contextos disponíveis no registro.\"\"\"
        return list(self._contexts.keys())
```

### 6. Configure API Endpoints

```python
# src/api/routes/analyze.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import os
import asyncio

from ...core.registry import ModelRegistry
from ...schemas.requests import AnalysisRequest
from ...schemas.responses import AnalysisResponse, AsyncAnalysisResponse
from ...exporters import get_exporter
from ...utils.storage import save_uploaded_file, get_result_path

router = APIRouter()
registry = ModelRegistry()

@router.post(\"/analyze\", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    model_id: str = \"object_detection\",
    model_version: str = \"latest\",
    context_name: str = \"tensorflow\"
):
    \"\"\"Endpoint para análise síncrona de uma imagem.\"\"\"
    # Salvar arquivo temporariamente
    file_path = await save_uploaded_file(file)
    
    try:
        # Obter modelo e contexto
        model_context = registry.create_model_context(model_id, model_version, context_name)
        if model_context is None:
            raise HTTPException(status_code=404, detail=f\"Modelo {model_id}@{model_version} não encontrado\")
        
        # Executar análise
        result = model_context.analyze(file_path)
        
        # Adicionar metadados da análise
        task_id = str(uuid.uuid4())
        result[\"task_id\"] = task_id
        result[\"status\"] = \"completed\"
        result[\"file_name\"] = file.filename
        
        return AnalysisResponse(
            task_id=task_id,
            status=\"completed\",
            results=result
        )
    finally:
        # Limpar arquivo temporário
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post(\"/analyze/async\", response_model=AsyncAnalysisResponse)
async def analyze_image_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_id: str = \"object_detection\",
    model_version: str = \"latest\",
    context_name: str = \"tensorflow\",
    export_format: Optional[str] = None
):
    \"\"\"Endpoint para análise assíncrona de uma imagem.\"\"\"
    # Gerar ID de tarefa
    task_id = str(uuid.uuid4())
    
    # Salvar arquivo para processamento posterior
    file_path = await save_uploaded_file(file, permanent=True)
    
    # Adicionar tarefa de análise em background
    background_tasks.add_task(
        process_analysis_task,
        task_id=task_id,
        file_path=file_path,
        model_id=model_id,
        model_version=model_version,
        context_name=context_name,
        file_name=file.filename,
        export_format=export_format
    )
    
    return AsyncAnalysisResponse(
        task_id=task_id,
        status=\"processing\",
        message=\"Análise iniciada em background\"
    )

async def process_analysis_task(
    task_id: str,
    file_path: str,
    model_id: str,
    model_version: str,
    context_name: str,
    file_name: str,
    export_format: Optional[str] = None
):
    \"\"\"Processa uma tarefa de análise em background.\"\"\"
    try:
        # Obter modelo e contexto
        model_context = registry.create_model_context(model_id, model_version, context_name)
        if model_context is None:
            raise ValueError(f\"Modelo {model_id}@{model_version} não encontrado\")
        
        # Executar análise
        result = model_context.analyze(file_path)
        
        # Adicionar metadados
        result[\"task_id\"] = task_id
        result[\"status\"] = \"completed\"
        result[\"file_name\"] = file_name
        
        # Salvar resultados
        result_path = get_result_path(task_id, \"json\")
        with open(result_path, 'w') as f:
            import json
            json.dump(result, f)
        
        # Exportar em formato específico se solicitado
        if export_format:
            exporter = get_exporter(export_format)
            if exporter:
                export_path = get_result_path(task_id, export_format)
                exporter.export(result, export_path)
    except Exception as e:
        # Registrar erro
        error_data = {
            \"task_id\": task_id,
            \"status\": \"failed\",
            \"error\": str(e)
        }
        error_path = get_result_path(task_id, \"error.json\")
        with open(error_path, 'w') as f:
            import json
            json.dump(error_data, f)
    finally:
        # Opcional: limpar arquivo de entrada após processamento
        if os.path.exists(file_path) and not os.environ.get(\"KEEP_INPUT_FILES\"):
            os.remove(file_path)

@router.get(\"/tasks/{task_id}\", response_model=AnalysisResponse)
async def get_task_result(task_id: str):
    \"\"\"Recupera o resultado de uma tarefa de análise.\"\"\"
    result_path = get_result_path(task_id, \"json\")
    error_path = get_result_path(task_id, \"error.json\")
    
    if os.path.exists(result_path):
        with open(result_path, 'r') as f:
            import json
            result = json.load(f)
        return AnalysisResponse(
            task_id=task_id,
            status=\"completed\",
            results=result
        )
    elif os.path.exists(error_path):
        with open(error_path, 'r') as f:
            import json
            error = json.load(f)
        raise HTTPException(
            status_code=500,
            detail=error.get(\"error\", \"Erro desconhecido durante processamento\")
        )
    else:
        return AnalysisResponse(
            task_id=task_id,
            status=\"processing\",
            results=None
        )

@router.get(\"/tasks/{task_id}/export/{format}\")
async def get_task_export(task_id: str, format: str):
    \"\"\"Recupera uma exportação específica do resultado de uma tarefa.\"\"\"
    export_path = get_result_path(task_id, format)
    
    if not os.path.exists(export_path):
        # Verificar se temos o resultado JSON e podemos exportar sob demanda
        result_path = get_result_path(task_id, \"json\")
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                import json
                result = json.load(f)
            
            exporter = get_exporter(format)
            if exporter:
                exporter.export(result, export_path)
            else:
                raise HTTPException(status_code=400, detail=f\"Formato de exportação não suportado: {format}\")
        else:
            raise HTTPException(status_code=404, detail=f\"Tarefa {task_id} não encontrada\")
    
    # Retornar arquivo de exportação
    from fastapi.responses import FileResponse
    return FileResponse(
        path=export_path,
        filename=f\"{task_id}.{format}\",
        media_type=f\"application/{format}\"
    )
```

## Como Usar o Serviço

### Inicialização do Serviço

1. **Configure o Ambiente:**
```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\\Scripts\\activate

# Instale dependências
pip install -r requirements.txt

# Baixe modelos pré-treinados
python scripts/download_models.py
```

2. **Inicie o Serviço:**
```bash
# Desenvolvimento
uvicorn src.main:app --reload

# Produção
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Integração com Aplicações Frontend

#### Análise Síncrona (JavaScript)
```javascript
async function analyzeImage(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    body: formData,
  });
  
  const result = await response.json();
  return result;
}

// Exemplo de uso
const fileInput = document.getElementById('image-input');
fileInput.addEventListener('change', async (event) => {
  const file = event.target.files[0];
  const result = await analyzeImage(file);
  
  // Exibir resultados na interface
  displayResults(result);
});
```

#### Análise Assíncrona (JavaScript)
```javascript
async function startAnalysis(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('export_format', 'csv');
  
  const response = await fetch('http://localhost:8000/api/analyze/async', {
    method: 'POST',
    body: formData,
  });
  
  const taskInfo = await response.json();
  return taskInfo.task_id;
}

async function checkAnalysisStatus(taskId) {
  const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`);
  return await response.json();
}

// Exemplo de uso
const fileInput = document.getElementById('image-input');
fileInput.addEventListener('change', async (event) => {
  const file = event.target.files[0];
  const taskId = await startAnalysis(file);
  
  // Polling para verificar o status da análise
  const checkStatus = setInterval(async () => {
    const status = await checkAnalysisStatus(taskId);
    if (status.status === 'completed') {
      clearInterval(checkStatus);
      displayResults(status.results);
      
      // Opcionalmente baixar resultados exportados
      downloadExport(taskId, 'csv');
    } else if (status.status === 'failed') {
      clearInterval(checkStatus);
      displayError(status.error);
    }
  }, 1000);
});

function downloadExport(taskId, format) {
  window.location.href = `http://localhost:8000/api/tasks/${taskId}/export/${format}`;
}
```

## Extensão do Serviço

### Adicionando um Novo Modelo

1. Crie uma nova classe de modelo que implemente a interface `ModelProtocol`:
```python
# src/models/image/segmentation.py
from typing import Any, Dict
import tensorflow as tf
import numpy as np
from ..base import BaseModel

class SegmentationModel(BaseModel[tf.Tensor, tf.Tensor]):
    \"\"\"Modelo para segmentação semântica de imagens.\"\"\"
    
    def __init__(self, model_id: str, version: str, model_path: str, class_mapping: Dict[int, str]):
        super().__init__(model_id, version)
        self.model_path = model_path
        self.class_mapping = class_mapping
        self._model = None
    
    # Implementar métodos preprocess, predict e postprocess...
```

2. Registre o modelo no sistema:
```python
# src/main.py
from src.core.registry import ModelRegistry
from src.core.context import TensorFlowContext
from src.models.image.segmentation import SegmentationModel

def setup_models():
    registry = ModelRegistry()
    
    # Registrar contextos
    registry.register_context(\"tensorflow\", TensorFlowContext())
    
    # Registrar modelos
    segmentation_model = SegmentationModel(
        model_id=\"semantic_segmentation\",
        version=\"1.0.0\",
        model_path=\"models_repository/segmentation/deeplabv3\",
        class_mapping={0: \"background\", 1: \"person\", 2: \"car\", ...}
    )
    registry.register_model(segmentation_model)
```

### Adicionando um Novo Exportador

1. Crie uma nova classe de exportador:
```python
# src/exporters/xlsx_exporter.py
from typing import Dict, Any
import pandas as pd
import os

class XlsxExporter:
    \"\"\"Exportador para formato Excel.\"\"\"
    
    @staticmethod
    def export(data: Dict[str, Any], output_path: str) -> str:
        \"\"\"Exporta resultados para um arquivo Excel.\"\"\"
        # Extrair e formatar dados para planilha
        if \"detections\" in data:
            df = pd.DataFrame(data[\"detections\"])
        else:
            # Tentar converter dados genéricos para DataFrame
            df = pd.json_normalize(data)
        
        # Salvar como Excel
        df.to_excel(output_path, index=False)
        return output_path
```

2. Registre o exportador:
```python
# src/exporters/__init__.py
from typing import Dict, Any, Optional
from .json_exporter import JsonExporter
from .csv_exporter import CsvExporter
from .xlsx_exporter import XlsxExporter

EXPORTERS = {
    \"json\": JsonExporter,
    \"csv\": CsvExporter,
    \"xlsx\": XlsxExporter
}

def get_exporter(format: str):
    \"\"\"Obtém um exportador pelo formato.\"\"\"
    return EXPORTERS.get(format)

def list_supported_formats():
    \"\"\"Lista formatos de exportação suportados.\"\"\"
    return list(EXPORTERS.keys())
```

## Próximos Passos

- **Implementar Autenticação**: Adicionar mecanismos para aut`
}
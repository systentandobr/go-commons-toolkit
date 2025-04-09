# Machine Learning Analysis Service

Serviço modular e extensível para análise de imagens e vídeos usando TensorFlow e técnicas avançadas de machine learning. O serviço implementa o padrão `@modelcontextprotocol` para facilitar a criação, carregamento e utilização de diferentes modelos de forma padronizada.

## Visão Geral

O serviço fornece uma API RESTful para analisar imagens e vídeos usando modelos de machine learning, com suporte para:

- Classificação de imagens
- Detecção de objetos
- Segmentação semântica
- Análise de vídeo

Os resultados podem ser exportados em diversos formatos (JSON, CSV) para consumo por aplicações frontend ou outros sistemas.

## Características Principais

- **Arquitetura Modular**: Baseada em princípios SOLID e clean architecture
- **Modelo Genérico**: Interface unificada para diferentes tipos de análise
- **Múltiplos Backends**: Suporte para TensorFlow, ONNX e PyTorch
- **API RESTful**: Endpoints para análise síncrona e assíncrona
- **Processamento Assíncrono**: Suporte para tarefas em background para arquivos grandes
- **Exportação Flexível**: Resultados disponíveis em diversos formatos
- **Monitoramento**: Métricas e logs para observabilidade

## Arquitetura

```
machinelearning-analysis-service/
├── src/
│   ├── core/           # Core do sistema
│   ├── models/         # Implementações de modelos
│   ├── processors/     # Processadores de entrada/saída
│   ├── api/            # Interface da API REST
│   ├── exporters/      # Exportadores de resultados
│   ├── schemas/        # Esquemas de dados
│   ├── utils/          # Utilitários
│   └── config/         # Configurações
├── tests/              # Testes automatizados
├── models_repository/  # Repositório local de modelos
└── scripts/            # Scripts utilitários
```

## Começando

### Pré-requisitos

- Python 3.9+
- TensorFlow 2.8+
- FastAPI 0.75+

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/sua-organizacao/machinelearning-analysis-service.git
   cd machinelearning-analysis-service
   ```

2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Baixe os modelos pré-treinados:
   ```bash
   python scripts/download_models.py
   ```

### Execução

1. Inicie o servidor:
   ```bash
   uvicorn src.main:app --reload
   ```

2. Acesse a documentação da API:
   ```
   http://localhost:8000/docs
   ```

### Uso via Docker

1. Construa a imagem:
   ```bash
   docker build -t ml-analysis-service .
   ```

2. Execute o contêiner:
   ```bash
   docker run -p 8000:8000 ml-analysis-service
   ```

## Exemplos de Uso

### Analisar uma imagem (detecção de objetos)

```python
import requests

url = "http://localhost:8000/api/analyze"
files = {"file": open("example.jpg", "rb")}
params = {"model_id": "generic_detector"}

response = requests.post(url, files=files, params=params)
results = response.json()

# Exibir resultados
for detection in results["results"]["detections"]:
    print(f"Objeto: {detection['class_name']}, Confiança: {detection['score']}")
```

### Processamento assíncrono de vídeo

```python
import requests
import time

# Iniciar análise assíncrona
url = "http://localhost:8000/api/analyze/async"
files = {"file": open("video.mp4", "rb")}
params = {
    "model_id": "generic_video_analyzer",
    "export_format": "json"
}

response = requests.post(url, files=files, params=params)
task = response.json()
task_id = task["task_id"]

# Verificar status da tarefa
while True:
    status_url = f"http://localhost:8000/api/tasks/{task_id}"
    status = requests.get(status_url).json()
    
    if status["status"] == "completed":
        print("Análise concluída!")
        print(status["results"])
        break
    elif status["status"] == "failed":
        print(f"Erro: {status.get('error')}")
        break
    
    print("Processando...")
    time.sleep(2)
```

## Extensão do Serviço

### Adicionando um Novo Modelo

Para adicionar um novo modelo, siga estas etapas:

1. Crie uma classe que estenda `BaseModel` ou `GenericModel`
2. Implemente os métodos `preprocess`, `predict` e `postprocess`
3. Registre o modelo no `ModelRegistry`

Exemplo:

```python
from src.models.generic.generic_model import GenericModel

# Criar instância do modelo
custom_model = GenericModel(
    model_id="my_custom_model",
    version="1.0.0",
    model_path="models_repository/my_model",
    task_type="classification",
    input_shape=[None, 224, 224, 3],
    preprocessing_config={
        "target_size": [224, 224],
        "normalize": True
    },
    postprocessing_config={
        "top_k": 5
    },
    metadata={
        "description": "Meu modelo personalizado",
        "class_labels": ["classe1", "classe2", "classe3"],
        "input_type": "image"
    }
)

# Registrar modelo
from src.core.registry import ModelRegistry
registry = ModelRegistry()
registry.register_model(custom_model)
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

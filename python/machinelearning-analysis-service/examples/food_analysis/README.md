# Caso de Uso: Análise Nutricional de Alimentos

Este exemplo demonstra como utilizar o serviço de análise de machine learning para identificar alimentos em imagens ou vídeos e fornecer informações nutricionais relevantes.

## Funcionalidades

O modelo implementado neste exemplo é capaz de:

1. **Identificar Alimentos**: Detectar e classificar diferentes tipos de alimentos em imagens ou frames de vídeo
2. **Avaliar Aparência**: Classificar o estado do alimento (saudável, estragado, etc.)
3. **Fornecer Dados Nutricionais**: Apresentar informações como calorias, macronutrientes, etc.
4. **Analisar Impacto na Saúde**: Determinar se o alimento é adequado para dietas específicas

## Arquitetura

O exemplo utiliza um modelo de duas etapas:
1. **Modelo de Detecção**: Para identificar alimentos na imagem (baseado em MobileNetV2 SSD)
2. **Modelo de Classificação**: Para analisar estado e características específicas (fine-tuned EfficientNet)

A base de dados nutricional é armazenada em um arquivo JSON que mapeia categorias de alimentos para suas informações nutricionais.

## Como Usar

### Configuração

Antes de utilizar este exemplo, você precisa baixar os modelos pré-treinados:

```bash
python examples/food_analysis/download_models.py
```

### API Example

```python
import requests

# Enviar uma imagem para análise
url = "http://localhost:8000/api/analyze"
files = {"file": open("examples/food_analysis/test_images/apple.jpg", "rb")}
params = {"model_id": "food_nutrition_analyzer"}

response = requests.post(url, files=files, params=params)
result = response.json()

# Exibir resultados
print(f"Alimentos identificados: {len(result['results']['food_items'])}")
for item in result['results']['food_items']:
    print(f"Alimento: {item['name']}")
    print(f"Confiança: {item['confidence']:.2f}")
    print(f"Estado: {item['condition']}")
    print(f"Calorias: {item['nutrition']['calories']} kcal")
    print(f"Proteínas: {item['nutrition']['protein']}g")
    print(f"Carboidratos: {item['nutrition']['carbs']}g")
    print(f"Gorduras: {item['nutrition']['fat']}g")
    print(f"Recomendação: {item['health_impact']}")
    print("-" * 30)
```

## Metodologia

O modelo foi treinado com um dataset que combina:
- Food-101 para classificação de alimentos
- Conjuntos de dados customizados para avaliação de condição dos alimentos
- Dados nutricionais da USDA National Nutrient Database

A análise de impacto na saúde é baseada em diretrizes nutricionais da OMS e outras organizações de saúde.

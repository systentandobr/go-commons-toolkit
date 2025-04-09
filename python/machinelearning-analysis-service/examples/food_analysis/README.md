# Exemplo de Análise Nutricional de Alimentos

## Visão Geral

Este exemplo demonstra o uso do serviço de análise nutricional de alimentos, mostrando como:
- Classificar alimentos em imagens
- Extrair informações nutricionais
- Gerar relatórios consolidados
- Exportar resultados em diferentes formatos

## Pré-requisitos

- Python 3.8+
- Bibliotecas:
  - TensorFlow
  - Pandas
  - OpenCV
  - Pydantic

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual
3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o Exemplo

```bash
python example_nutrition_analysis.py
```

## Recursos

- Análise de múltiplos alimentos
- Geração de relatório nutricional
- Exportação em formatos:
  - JSON
  - CSV 
  - Excel

## Estrutura do Exemplo

- `example_nutrition_analysis.py`: Script principal de demonstração
- `resources/food_images/`: Diretório com imagens de exemplo
- `outputs/`: Diretório para resultados exportados

## Como Funciona

1. Carrega imagens de alimentos
2. Classifica cada alimento
3. Extrai informações nutricionais
4. Gera relatório consolidado
5. Exporta resultados em múltiplos formatos

## Limitações

- Modelo de demonstração com conjunto limitado de alimentos
- Requer imagens de alta qualidade
- Precisão depende do modelo de treinamento

## Próximos Passos

- Treinar modelo com conjunto de dados mais abrangente
- Adicionar mais tipos de alimentos
- Melhorar precisão de classificação

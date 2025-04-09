#!/usr/bin/env python3
"""
Script para benchmark de modelos de machine learning.

Este script executa testes de desempenho em diferentes modelos para avaliar
tempo de execução, uso de memória e precisão.
"""

import os
import sys
import argparse
import logging
import time
import json
import numpy as np
from pathlib import Path
import tensorflow as tf
from tqdm import tqdm

# Configurar paths para importar módulos do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core.registry import ModelRegistry
from src.core.context import TensorFlowContext, ONNXContext, PyTorchContext

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Diretório para salvar resultados
RESULTS_DIR = os.path.join(project_root, "benchmark_results")


def load_test_images(image_dir, size=(224, 224), batch_size=1, num_images=None):
    """
    Carrega imagens para teste.
    
    Args:
        image_dir: Diretório contendo imagens
        size: Tamanho para redimensionamento
        batch_size: Tamanho do lote
        num_images: Número máximo de imagens a carregar
        
    Returns:
        Tensor com imagens de teste
    """
    logger.info(f"Carregando imagens de teste de {image_dir}")
    
    image_paths = []
    valid_extensions = ['.jpg', '.jpeg', '.png']
    
    # Listar arquivos de imagem
    for ext in valid_extensions:
        image_paths.extend(list(Path(image_dir).glob(f'*{ext}')))
    
    if num_images:
        image_paths = image_paths[:num_images]
    
    if not image_paths:
        logger.error(f"Nenhuma imagem encontrada em {image_dir}")
        return None
    
    logger.info(f"Carregando {len(image_paths)} imagens")
    
    # Carregar e pré-processar imagens
    images = []
    for path in tqdm(image_paths, desc="Carregando imagens"):
        try:
            img = tf.io.read_file(str(path))
            img = tf.image.decode_image(img, channels=3, expand_animations=False)
            img = tf.image.resize(img, size)
            img = tf.cast(img, tf.float32) / 255.0
            images.append(img)
        except Exception as e:
            logger.warning(f"Erro ao carregar imagem {path}: {e}")
    
    # Converter para batch
    return tf.stack(images)


def benchmark_model(model_id, version, context_name, batch_size=1, num_runs=10, image_dir=None):
    """
    Executa benchmark de um modelo.
    
    Args:
        model_id: ID do modelo
        version: Versão do modelo
        context_name: Nome do contexto
        batch_size: Tamanho do lote
        num_runs: Número de execuções
        image_dir: Diretório com imagens de teste
        
    Returns:
        Dict com resultados do benchmark
    """
    logger.info(f"Iniciando benchmark do modelo {model_id}@{version} com contexto {context_name}")
    
    # Obter modelo e contexto
    registry = ModelRegistry()
    model_context = registry.create_model_context(model_id, version, context_name)
    
    if not model_context:
        logger.error(f"Modelo {model_id}@{version} ou contexto {context_name} não encontrado")
        return None
    
    # Preparar dados de teste
    if image_dir:
        # Usar imagens reais
        test_data = load_test_images(image_dir, batch_size=batch_size)
    else:
        # Gerar dados sintéticos
        input_shape = getattr(model_context.model, 'input_shape', [None, 224, 224, 3])
        shape = [batch_size] + input_shape[1:]
        test_data = tf.random.uniform(shape, 0, 1)
    
    # Executar warmup
    logger.info("Executando warmup...")
    _ = model_context.analyze(test_data)
    
    # Executar benchmark
    logger.info(f"Executando {num_runs} iterações...")
    
    times = []
    for i in tqdm(range(num_runs), desc="Benchmark"):
        start_time = time.time()
        result = model_context.analyze(test_data)
        elapsed = time.time() - start_time
        times.append(elapsed)
    
    # Calcular estatísticas
    times = np.array(times)
    stats = {
        "model_id": model_id,
        "version": version,
        "context": context_name,
        "batch_size": batch_size,
        "num_runs": num_runs,
        "mean_time": float(np.mean(times)),
        "median_time": float(np.median(times)),
        "min_time": float(np.min(times)),
        "max_time": float(np.max(times)),
        "std_time": float(np.std(times)),
        "throughput": float(batch_size / np.mean(times)),  # imagens/segundo
    }
    
    logger.info(f"Benchmark concluído - Tempo médio: {stats['mean_time']:.4f}s, Throughput: {stats['throughput']:.2f} img/s")
    
    return stats


def save_results(results, output_dir=RESULTS_DIR):
    """
    Salva resultados do benchmark.
    
    Args:
        results: Dicionário com resultados
        output_dir: Diretório para salvar resultados
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(output_dir, f"benchmark_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Resultados salvos em {output_file}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Benchmark de modelos de ML")
    parser.add_argument("--model-id", type=str, required=True,
                        help="ID do modelo a avaliar")
    parser.add_argument("--version", type=str, default="latest",
                        help="Versão do modelo (padrão: latest)")
    parser.add_argument("--context", type=str, default="tensorflow",
                        help="Contexto de execução (padrão: tensorflow)")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="Tamanho do lote (padrão: 1)")
    parser.add_argument("--num-runs", type=int, default=10,
                        help="Número de execuções (padrão: 10)")
    parser.add_argument("--image-dir", type=str, default=None,
                        help="Diretório com imagens de teste")
    parser.add_argument("--output-dir", type=str, default=RESULTS_DIR,
                        help="Diretório para salvar resultados")
    
    args = parser.parse_args()
    
    # Executar benchmark
    results = benchmark_model(
        model_id=args.model_id,
        version=args.version,
        context_name=args.context,
        batch_size=args.batch_size,
        num_runs=args.num_runs,
        image_dir=args.image_dir
    )
    
    if results:
        save_results(results, args.output_dir)


if __name__ == "__main__":
    main()

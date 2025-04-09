#!/usr/bin/env python3
"""
Script para baixar modelos pré-treinados para o serviço de análise.

Este script verifica se os modelos necessários existem e, caso contrário,
faz o download deles do TensorFlow Hub ou outras fontes.
"""

import os
import sys
import argparse
import logging
import zipfile
import tarfile
import shutil
from pathlib import Path
from urllib.request import urlretrieve
from tqdm import tqdm
import tensorflow as tf

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Diretório para salvar os modelos
MODELS_DIR = os.environ.get("MODELS_DIR", "models_repository")

# Lista de modelos a serem baixados
# Formato: (nome, url, tipo)
MODELS = [
    (
        "mobilenet_v2",
        "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4",
        "tfhub"
    ),
    (
        "ssd_mobilenet_v2",
        "https://tfhub.dev/tensorflow/ssd_mobilenet_v2/2",
        "tfhub"
    ),
    (
        "deeplabv3",
        "https://tfhub.dev/tensorflow/deeplabv3/1",
        "tfhub"
    ),
]


class DownloadProgressBar(tqdm):
    """Barra de progresso para download de arquivos."""
    
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        Atualiza a barra de progresso.
        
        Args:
            b: Número do bloco
            bsize: Tamanho do bloco
            tsize: Tamanho total
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    """
    Baixa um arquivo da web com barra de progresso.
    
    Args:
        url: URL do arquivo
        output_path: Caminho para salvar o arquivo
    """
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urlretrieve(url, filename=output_path, reporthook=t.update_to)


def download_tfhub_model(model_name, model_url):
    """
    Baixa um modelo do TensorFlow Hub.
    
    Args:
        model_name: Nome do modelo
        model_url: URL do modelo no TensorFlow Hub
        
    Returns:
        bool: True se o download foi bem-sucedido, False caso contrário
    """
    model_dir = os.path.join(MODELS_DIR, model_name)
    
    # Verificar se o modelo já existe
    if os.path.exists(model_dir) and os.listdir(model_dir):
        logger.info(f"Modelo {model_name} já existe em {model_dir}")
        return True
    
    # Criar diretório para o modelo
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        # Baixar e salvar o modelo
        logger.info(f"Baixando modelo {model_name} de {model_url}")
        model = tf.saved_model.load(model_url)
        tf.saved_model.save(model, model_dir)
        logger.info(f"Modelo {model_name} salvo em {model_dir}")
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar modelo {model_name}: {e}")
        # Limpar diretório em caso de erro
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
        return False


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Download de modelos pré-treinados")
    parser.add_argument("--models-dir", type=str, default=MODELS_DIR,
                        help=f"Diretório para salvar os modelos (padrão: {MODELS_DIR})")
    parser.add_argument("--force", action="store_true",
                        help="Força o download mesmo que o modelo já exista")
    args = parser.parse_args()
    
    # Atualizar diretório de modelos
    global MODELS_DIR
    MODELS_DIR = args.models_dir
    
    # Criar diretório de modelos se não existir
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Baixar cada modelo
    success_count = 0
    for model_name, model_url, model_type in MODELS:
        model_dir = os.path.join(MODELS_DIR, model_name)
        
        # Verificar se o modelo já existe
        if not args.force and os.path.exists(model_dir) and os.listdir(model_dir):
            logger.info(f"Modelo {model_name} já existe em {model_dir}")
            success_count += 1
            continue
        
        # Limpar diretório existente se force=True
        if args.force and os.path.exists(model_dir):
            logger.info(f"Removendo modelo existente {model_name}")
            shutil.rmtree(model_dir)
        
        # Baixar modelo conforme o tipo
        if model_type == "tfhub":
            if download_tfhub_model(model_name, model_url):
                success_count += 1
        else:
            logger.error(f"Tipo de modelo não suportado: {model_type}")
    
    # Relatório final
    logger.info(f"Download concluído: {success_count}/{len(MODELS)} modelos baixados com sucesso")
    
    if success_count < len(MODELS):
        sys.exit(1)


if __name__ == "__main__":
    main()

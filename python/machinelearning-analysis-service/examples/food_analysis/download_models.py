#!/usr/bin/env python3
"""
Script para download dos modelos necessários para análise nutricional.

Este script baixa os modelos pré-treinados para classificação de alimentos e
avaliação de condição, salvando-os no diretório de modelos do serviço.
"""

import os
import sys
import shutil
import argparse
import logging
import zipfile
import tarfile
from pathlib import Path
from urllib.request import urlretrieve
from tqdm import tqdm

# Configurar path para incluir a raiz do projeto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.environ.get("MODELS_DIR", "models_repository"), "food_nutrition_analyzer")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# URLs para download dos modelos
# Em produção, estes seriam URLs para modelos reais
MODELS = [
    {
        "name": "food_classifier",
        "url": "https://storage.googleapis.com/example-models/food_classifier.tar.gz",
        "fallback_url": "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification/5",
        "format": "tf_hub",
        "version": "1.0.0",
        "description": "Modelo de classificação de alimentos baseado em MobileNetV2"
    },
    {
        "name": "food_condition_classifier",
        "url": "https://storage.googleapis.com/example-models/food_condition.tar.gz",
        "fallback_url": "https://tfhub.dev/google/imagenet/efficientnet_b0/classification/1",
        "format": "tf_hub",
        "version": "1.0.0",
        "description": "Modelo para avaliação de condição de alimentos baseado em EfficientNet"
    }
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


def download_from_url(url, output_path):
    """
    Baixa um arquivo da web com barra de progresso.
    
    Args:
        url: URL do arquivo
        output_path: Caminho para salvar o arquivo
    """
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urlretrieve(url, filename=output_path, reporthook=t.update_to)


def download_from_tf_hub(model_url, output_dir):
    """
    Baixa e salva um modelo do TensorFlow Hub.
    
    Args:
        model_url: URL do modelo no TF Hub
        output_dir: Diretório para salvar o modelo
        
    Returns:
        bool: True se o download foi bem-sucedido, False caso contrário
    """
    try:
        import tensorflow as tf
        import tensorflow_hub as hub
        
        logger.info(f"Baixando modelo de {model_url}")
        model = hub.load(model_url)
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar modelo
        tf.saved_model.save(model, output_dir)
        logger.info(f"Modelo salvo em {output_dir}")
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar modelo do TF Hub: {e}")
        return False


def extract_archive(archive_path, output_dir, format="auto"):
    """
    Extrai um arquivo compactado.
    
    Args:
        archive_path: Caminho para o arquivo
        output_dir: Diretório para extrair
        format: Formato do arquivo ('auto', 'zip', 'tar')
        
    Returns:
        bool: True se a extração foi bem-sucedida, False caso contrário
    """
    try:
        # Determinar formato automaticamente
        if format == "auto":
            if archive_path.endswith('.zip'):
                format = 'zip'
            elif archive_path.endswith(('.tar.gz', '.tgz')):
                format = 'tar'
            else:
                logger.error(f"Formato não suportado: {archive_path}")
                return False
        
        # Extrair conforme formato
        if format == 'zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
        elif format == 'tar':
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(output_dir)
        else:
            logger.error(f"Formato não suportado: {format}")
            return False
        
        logger.info(f"Arquivo extraído em {output_dir}")
        return True
    except Exception as e:
        logger.error(f"Erro ao extrair arquivo: {e}")
        return False


def main():
    """Função principal para download dos modelos."""
    parser = argparse.ArgumentParser(description="Download de modelos para análise nutricional")
    parser.add_argument("--models-dir", type=str, default=MODELS_DIR,
                        help=f"Diretório para salvar os modelos")
    parser.add_argument("--force", action="store_true",
                        help="Força o download mesmo que o modelo já exista")
    parser.add_argument("--use-fallback", action="store_true",
                        help="Usa URL alternativa do TF Hub caso a principal falhe")
    args = parser.parse_args()
    
    # Criar diretórios necessários
    os.makedirs(args.models_dir, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Baixar cada modelo
    downloaded_models = 0
    
    for model in MODELS:
        model_dir = os.path.join(args.models_dir, model["name"])
        
        # Verificar se o modelo já existe
        if not args.force and os.path.exists(model_dir) and os.listdir(model_dir):
            logger.info(f"Modelo {model['name']} já existe em {model_dir}")
            downloaded_models += 1
            continue
        
        # Limpar diretório se existir e force=True
        if args.force and os.path.exists(model_dir):
            logger.info(f"Removendo modelo existente {model['name']}")
            shutil.rmtree(model_dir)
        
        # Tentativa 1: Usar URL principal
        success = False
        temp_path = os.path.join(TEMP_DIR, f"{model['name']}.tar.gz")
        
        try:
            logger.info(f"Baixando modelo {model['name']} de {model['url']}")
            download_from_url(model['url'], temp_path)
            
            # Extrair arquivo
            os.makedirs(model_dir, exist_ok=True)
            success = extract_archive(temp_path, model_dir)
        except Exception as e:
            logger.warning(f"Falha ao baixar modelo principal: {e}")
            success = False
        
        # Tentativa 2: Usar TF Hub (fallback)
        if not success and args.use_fallback and model.get("fallback_url"):
            logger.info(f"Tentando URL alternativa: {model['fallback_url']}")
            success = download_from_tf_hub(model['fallback_url'], model_dir)
        
        if success:
            downloaded_models += 1
            logger.info(f"Modelo {model['name']} baixado com sucesso")
        else:
            logger.error(f"Falha ao baixar modelo {model['name']}")
            
            # Criar placeholder para desenvolvimento
            create_placeholder_model(model_dir, model)
            logger.warning(f"Criado modelo placeholder para {model['name']}")
            downloaded_models += 1
    
    # Limpar diretório temporário
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    
    # Relatório final
    if downloaded_models == len(MODELS):
        logger.info(f"Todos os {len(MODELS)} modelos foram baixados/preparados com sucesso!")
        return 0
    else:
        logger.warning(f"Baixados {downloaded_models}/{len(MODELS)} modelos")
        return 1


def create_placeholder_model(model_dir, model_info):
    """
    Cria um modelo placeholder para desenvolvimento quando o download falha.
    
    Args:
        model_dir: Diretório para salvar o modelo
        model_info: Informações sobre o modelo
    """
    try:
        import tensorflow as tf
        
        # Criar diretório
        os.makedirs(model_dir, exist_ok=True)
        
        # Criar modelo dummy baseado no formato esperado
        if model_info["name"] == "food_classifier":
            # Modelo de classificação com 10 classes
            inputs = tf.keras.Input(shape=(224, 224, 3))
            x = tf.keras.layers.Conv2D(8, 3, activation='relu')(inputs)
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            outputs = tf.keras.layers.Dense(10)(x)
            model = tf.keras.Model(inputs, outputs)
        else:
            # Modelo de condição com 8 classes
            inputs = tf.keras.Input(shape=(224, 224, 3))
            x = tf.keras.layers.Conv2D(8, 3, activation='relu')(inputs)
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            outputs = tf.keras.layers.Dense(8)(x)
            model = tf.keras.Model(inputs, outputs)
        
        # Salvar modelo
        tf.saved_model.save(model, model_dir)
        
        # Criar README com informações
        readme_path = os.path.join(model_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(f"# {model_info['name']} (Placeholder)\n\n")
            f.write(f"Este é um modelo placeholder criado automaticamente.\n")
            f.write(f"Versão: {model_info['version']}\n")
            f.write(f"Descrição: {model_info['description']}\n\n")
            f.write(f"Nota: Este é um modelo simplificado para fins de desenvolvimento,\n")
            f.write(f"não adequado para uso em produção.\n")
    
    except Exception as e:
        logger.error(f"Erro ao criar modelo placeholder: {e}")
        
        # Criar diretório com arquivo de info como fallback
        os.makedirs(model_dir, exist_ok=True)
        with open(os.path.join(model_dir, "info.txt"), 'w') as f:
            f.write(f"Model placeholder: {model_info['name']}\n")
            f.write(f"Error creating model: {str(e)}\n")


if __name__ == "__main__":
    sys.exit(main())

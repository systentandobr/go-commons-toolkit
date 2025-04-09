#!/usr/bin/env python3
"""
Script para inicializar o projeto do Agente Autônomo de E-commerce
Simplifica a configuração inicial e execução para desenvolvimento
"""

import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é adequada."""
    if sys.version_info < (3, 10):
        print("Este projeto requer Python 3.10 ou superior.")
        sys.exit(1)
    print("✅ Versão do Python OK")

def setup_environment(dev_mode=True):
    """Configura o ambiente de desenvolvimento."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Criando arquivo .env a partir do .env.example...")
            with open(".env.example", "r") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            print("✅ Arquivo .env criado")
        else:
            print("❌ Arquivo .env.example não encontrado")
            sys.exit(1)
    else:
        print("✅ Arquivo .env já existe")

    # Criar diretórios necessários se não existirem
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def install_dependencies(dev_mode=True):
    """Instala as dependências do projeto."""
    print("Instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Falha ao instalar dependências")
        sys.exit(1)

def run_development_server():
    """Executa o servidor de desenvolvimento."""
    print("Iniciando servidor de desenvolvimento...")
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload"], check=True)
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo usuário")
    except subprocess.CalledProcessError:
        print("❌ Falha ao iniciar o servidor")
        sys.exit(1)

def run_docker_compose():
    """Executa o ambiente usando Docker Compose."""
    print("Iniciando serviços com Docker Compose...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Serviços Docker iniciados com sucesso")
        print("Para visualizar logs: docker-compose logs -f")
        print("Para parar os serviços: docker-compose down")
    except subprocess.CalledProcessError:
        print("❌ Falha ao iniciar serviços Docker")
        sys.exit(1)

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Utilitário de setup para o Agente Autônomo de E-commerce")
    parser.add_argument("--docker", action="store_true", help="Usar Docker em vez do ambiente local")
    parser.add_argument("--setup-only", action="store_true", help="Apenas configurar o ambiente sem executar o servidor")
    args = parser.parse_args()

    print("=" * 80)
    print("Configuração do Agente Autônomo de E-commerce")
    print("=" * 80)

    # Verificar versão do Python
    check_python_version()

    # Configurar ambiente
    setup_environment()

    # Se não estiver usando Docker, instalar dependências localmente
    if not args.docker:
        install_dependencies()

    if args.setup_only:
        print("✅ Configuração concluída. Execute 'python run.py' para iniciar o servidor.")
        return

    # Executar servidor ou docker
    if args.docker:
        run_docker_compose()
    else:
        run_development_server()

if __name__ == "__main__":
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()

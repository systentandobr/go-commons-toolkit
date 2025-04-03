#!/bin/bash

# Script de inicialização do Go Commons Toolkit
# Este script configura o ambiente de desenvolvimento para o projeto

set -e

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para exibir mensagens de erro e sair
error() {
    echo -e "${RED}Erro: $1${NC}" >&2
    exit 1
}

# Função para exibir mensagens de sucesso
success() {
    echo -e "${GREEN}$1${NC}"
}

# Função para exibir mensagens informativas
info() {
    echo -e "${BLUE}$1${NC}"
}

# Função para exibir avisos
warning() {
    echo -e "${YELLOW}Aviso: $1${NC}"
}

# Verifica se Go está instalado
check_go() {
    info "Verificando se Go está instalado..."
    if ! command -v go &> /dev/null; then
        error "Go não está instalado. Por favor, instale o Go antes de continuar."
    fi
    
    go_version=$(go version | awk '{print $3}' | sed 's/go//')
    min_version="1.19"
    
    if ! [[ "$(printf '%s\n' "$min_version" "$go_version" | sort -V | head -n1)" = "$min_version" ]]; then
        warning "Versão mínima recomendada do Go é $min_version. Você está usando $go_version."
    else
        success "Go $go_version está instalado."
    fi
}

# Verifica se Docker está instalado
check_docker() {
    info "Verificando se Docker está instalado..."
    if ! command -v docker &> /dev/null; then
        warning "Docker não está instalado. Alguns recursos podem não funcionar corretamente."
    else
        success "Docker está instalado."
    fi
    
    info "Verificando se Docker Compose está instalado..."
    if ! command -v docker-compose &> /dev/null; then
        warning "Docker Compose não está instalado. Alguns recursos podem não funcionar corretamente."
    else
        success "Docker Compose está instalado."
    fi
}

# Configura o arquivo .env
setup_env() {
    info "Configurando arquivo .env..."
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            success "Arquivo .env criado com base no .env.example."
        else
            warning "Arquivo .env.example não encontrado. Criando .env com valores padrão."
            cat > .env << EOL
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE_NAME=my_database

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVER=localhost:9092
KAFKA_CONSUMER_GROUP_ID=my-consumer-group
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_ENABLE_AUTO_COMMIT=true

# Supabase/PostgreSQL Configuration
SUPABASE_URI=postgresql://localhost:5432
SUPABASE_DATABASE=postgres
SUPABASE_USERNAME=postgres
SUPABASE_PASSWORD=postgres

# HTTP Server Configuration
HTTP_PORT=8080
TIMEOUT_SECONDS=30
EOL
            success "Arquivo .env criado com valores padrão."
        fi
    else
        info "Arquivo .env já existe."
    fi
}

# Instala dependências do projeto
install_deps() {
    info "Instalando dependências do projeto..."
    go mod download
    go mod tidy
    success "Dependências instaladas com sucesso."
}

# Instala ferramentas de desenvolvimento
install_tools() {
    info "Instalando ferramentas de desenvolvimento..."
    
    # Golangci-lint
    if ! command -v golangci-lint &> /dev/null; then
        info "Instalando golangci-lint..."
        go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    else
        info "golangci-lint já está instalado."
    fi
    
    # Mockgen
    if ! command -v mockgen &> /dev/null; then
        info "Instalando mockgen..."
        go install github.com/golang/mock/mockgen@latest
    else
        info "mockgen já está instalado."
    fi
    
    success "Ferramentas de desenvolvimento instaladas com sucesso."
}

# Inicia os serviços Docker
start_services() {
    info "Iniciando serviços Docker..."
    if [ -f docker-compose.yml ]; then
        docker-compose up -d
        success "Serviços Docker iniciados com sucesso."
    else
        warning "Arquivo docker-compose.yml não encontrado. Pulando inicialização de serviços."
    fi
}

# Executar testes
run_tests() {
    info "Executando testes..."
    go test -short ./...
    success "Testes executados com sucesso."
}

# Menu principal
main() {
    echo "======================================================"
    echo "  Inicialização do Go Commons Toolkit"
    echo "======================================================"
    
    check_go
    check_docker
    setup_env
    install_deps
    
    echo
    read -p "Deseja instalar as ferramentas de desenvolvimento? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_tools
    fi
    
    echo
    read -p "Deseja iniciar os serviços Docker? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
    fi
    
    echo
    read -p "Deseja executar os testes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    echo
    success "Inicialização concluída com sucesso!"
    echo
    info "Para começar a utilizar o Go Commons Toolkit, consulte a documentação."
    info "Execute 'make help' para ver os comandos disponíveis."
    echo
}

# Executa o menu principal
main "$@"

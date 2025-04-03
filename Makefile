.PHONY: build test clean examples lint docker-up docker-down

# Variáveis
BINARY_NAME=toolkit
EXAMPLES_DIR=./cmd/examples
BUILD_DIR=./build
TEST_FLAGS=-v -race -coverprofile=coverage.out
LINT_FLAGS=--enable=misspell,gosec,govet,staticcheck,unused,gocritic --deadline=5m

# Comando padrão
all: clean build test

# Compilar todos os binários
build:
	@echo "Compilando binários..."
	@mkdir -p $(BUILD_DIR)
	@go build -o $(BUILD_DIR)/$(BINARY_NAME)-http-example ./cmd/examples/http
	@echo "Binários compilados com sucesso."

# Compilar todos os exemplos
build-examples:
	@echo "Compilando exemplos..."
	@mkdir -p $(BUILD_DIR)/examples
	@for dir in $$(find $(EXAMPLES_DIR) -type d -mindepth 1 -maxdepth 2); do \
		example_name=$$(basename $$dir); \
		if [ -f $$dir/main.go ]; then \
			echo "Compilando exemplo: $$example_name"; \
			go build -o $(BUILD_DIR)/examples/$$example_name $$dir; \
		fi; \
	done

# Executar testes
test:
	@echo "Executando testes..."
	@go test $(TEST_FLAGS) ./...
	@go tool cover -html=coverage.out -o coverage.html

# Executar testes de integração
integration-test:
	@echo "Executando testes de integração..."
	@go test -tags=integration $(TEST_FLAGS) ./test/...

# Limpar arquivos de build
clean:
	@echo "Limpando arquivos de build..."
	@rm -rf $(BUILD_DIR)
	@rm -f coverage.out coverage.html

# Executar o linter
lint:
	@echo "Executando linter..."
	@which golangci-lint > /dev/null || go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@golangci-lint run $(LINT_FLAGS) ./...

# Iniciar ambiente Docker
docker-up:
	@echo "Iniciando ambiente Docker..."
	@docker-compose up -d

# Parar ambiente Docker
docker-down:
	@echo "Parando ambiente Docker..."
	@docker-compose down

# Criar arquivo .env a partir do exemplo
setup-env:
	@echo "Configurando arquivo .env..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env criado com sucesso a partir de .env.example"; \
	else \
		echo ".env já existe"; \
	fi

# Instalar dependências
deps:
	@echo "Instalando dependências..."
	@go mod download
	@go mod tidy

# Executar exemplo HTTP
run-http-example:
	@echo "Executando exemplo HTTP..."
	@go run $(EXAMPLES_DIR)/http/main.go

# Executar exemplo de produtor Kafka
run-kafka-producer:
	@echo "Executando exemplo de produtor Kafka..."
	@go run $(EXAMPLES_DIR)/kafka/producer/main.go

# Executar exemplo de consumidor Kafka
run-kafka-consumer:
	@echo "Executando exemplo de consumidor Kafka..."
	@go run $(EXAMPLES_DIR)/kafka/consumer/main.go

# Executar exemplo MongoDB
run-mongodb-example:
	@echo "Executando exemplo MongoDB..."
	@go run $(EXAMPLES_DIR)/mongodb/main.go

# Executar exemplo Supabase
run-supabase-example:
	@echo "Executando exemplo Supabase..."
	@go run $(EXAMPLES_DIR)/supabase/main.go

# Executar gerador de projetos
run-project-generator:
	@echo "Executando gerador de projetos..."
	@go run $(EXAMPLES_DIR)/project-generator/main.go

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make build             - Compila o binário principal"
	@echo "  make build-examples    - Compila todos os exemplos"
	@echo "  make test              - Executa os testes"
	@echo "  make integration-test  - Executa testes de integração"
	@echo "  make clean             - Remove arquivos de build"
	@echo "  make lint              - Executa o linter"
	@echo "  make docker-up         - Inicia ambiente Docker"
	@echo "  make docker-down       - Para ambiente Docker"
	@echo "  make setup-env         - Cria arquivo .env a partir do exemplo"
	@echo "  make deps              - Instala dependências"
	@echo "  make run-http-example  - Executa exemplo HTTP"
	@echo "  make run-kafka-producer- Executa exemplo de produtor Kafka"
	@echo "  make run-kafka-consumer- Executa exemplo de consumidor Kafka"
	@echo "  make run-mongodb-example- Executa exemplo MongoDB"
	@echo "  make run-supabase-example- Executa exemplo Supabase"
	@echo "  make run-project-generator- Executa gerador de projetos"

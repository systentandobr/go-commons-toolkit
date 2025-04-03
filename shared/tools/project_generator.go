package tools

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"text/template"
)

// SchemaGenerator gera arquivos de esquema para diferentes componentes do sistema
type SchemaGenerator struct {
	BaseDir   string
	Templates map[string]string
}

// NewSchemaGenerator cria um novo gerador de esquemas
func NewSchemaGenerator(baseDir string) *SchemaGenerator {
	return &SchemaGenerator{
		BaseDir:   baseDir,
		Templates: defaultTemplates(),
	}
}

// defaultTemplates retorna os templates padrão para geração de esquemas
func defaultTemplates() map[string]string {
	return map[string]string{
		"entity": `package entity

// {{.Name}} representa {{.Description}}
type {{.Name}} struct {
	{{range .Fields}}{{.Name}} {{.Type}} {{.Tags}}
	{{end}}
}

{{range .Methods}}
// {{.Name}} {{.Description}}
func (e *{{$.Name}}) {{.Name}}({{.Params}}) {{.Returns}} {
	{{.Body}}
}
{{end}}`,
		"repository": `package repository

import (
	"context"

	"github.com/systentandobr/go-commons-toolkit/internal/domain/{{.DomainName}}/entity"
)

// {{.Name}}Repository define as operações para repositório de {{.EntityName}}
type {{.Name}}Repository interface {
	// Operações básicas
	FindByID(ctx context.Context, id string) (*entity.{{.EntityName}}, error)
	FindAll(ctx context.Context, filter map[string]interface{}) ([]*entity.{{.EntityName}}, error)
	Save(ctx context.Context, entity *entity.{{.EntityName}}) error
	Update(ctx context.Context, entity *entity.{{.EntityName}}) error
	Delete(ctx context.Context, id string) error

	// Operações específicas
	{{range .CustomMethods}}
	{{.Name}}({{.Params}}) {{.Returns}}
	{{end}}
}`,
		"service": `package service

import (
	"context"

	"github.com/systentandobr/go-commons-toolkit/internal/domain/{{.DomainName}}/entity"
	"github.com/systentandobr/go-commons-toolkit/internal/domain/{{.DomainName}}/repository"
)

// {{.Name}}Service representa o serviço de domínio para {{.EntityName}}
type {{.Name}}Service struct {
	repo repository.{{.EntityName}}Repository
}

// New{{.Name}}Service cria uma nova instância do serviço de {{.EntityName}}
func New{{.Name}}Service(repo repository.{{.EntityName}}Repository) *{{.Name}}Service {
	return &{{.Name}}Service{
		repo: repo,
	}
}

// GetByID obtém um {{.EntityName}} pelo ID
func (s *{{.Name}}Service) GetByID(ctx context.Context, id string) (*entity.{{.EntityName}}, error) {
	return s.repo.FindByID(ctx, id)
}

// GetAll obtém todos os {{.EntityName}}s com base no filtro
func (s *{{.Name}}Service) GetAll(ctx context.Context, filter map[string]interface{}) ([]*entity.{{.EntityName}}, error) {
	return s.repo.FindAll(ctx, filter)
}

// Create cria um novo {{.EntityName}}
func (s *{{.Name}}Service) Create(ctx context.Context, e *entity.{{.EntityName}}) error {
	return s.repo.Save(ctx, e)
}

// Update atualiza um {{.EntityName}} existente
func (s *{{.Name}}Service) Update(ctx context.Context, e *entity.{{.EntityName}}) error {
	return s.repo.Update(ctx, e)
}

// Delete exclui um {{.EntityName}} pelo ID
func (s *{{.Name}}Service) Delete(ctx context.Context, id string) error {
	return s.repo.Delete(ctx, id)
}

{{range .CustomMethods}}
// {{.Name}} {{.Description}}
func (s *{{$.Name}}Service) {{.Name}}({{.Params}}) {{.Returns}} {
	{{.Body}}
}
{{end}}`,
		"mongo_repository": `package mongodb

import (
	"context"
	"errors"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"

	"github.com/systentandobr/go-commons-toolkit/internal/domain/{{.DomainName}}/entity"
	"github.com/systentandobr/go-commons-toolkit/internal/domain/{{.DomainName}}/repository"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/persistence/mongodb"
)

// Mongo{{.EntityName}}Repository implementa o repositório de {{.EntityName}} usando MongoDB
type Mongo{{.EntityName}}Repository struct {
	collection *mongodb.Collection
}

// NewMongo{{.EntityName}}Repository cria um novo repositório de {{.EntityName}} MongoDB
func NewMongo{{.EntityName}}Repository(collectionName string) (repository.{{.EntityName}}Repository, error) {
	collection, err := mongodb.NewCollection(collectionName)
	if err != nil {
		return nil, err
	}

	return &Mongo{{.EntityName}}Repository{
		collection: collection,
	}, nil
}

// FindByID busca um {{.EntityName}} pelo ID
func (r *Mongo{{.EntityName}}Repository) FindByID(ctx context.Context, id string) (*entity.{{.EntityName}}, error) {
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return nil, err
	}

	var result entity.{{.EntityName}}
	err = r.collection.FindOne(ctx, bson.M{"_id": objectID}, &result)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return nil, nil
		}
		return nil, err
	}

	return &result, nil
}

// FindAll busca todos os {{.EntityName}}s com base no filtro
func (r *Mongo{{.EntityName}}Repository) FindAll(ctx context.Context, filter map[string]interface{}) ([]*entity.{{.EntityName}}, error) {
	bsonFilter := bson.M{}
	for k, v := range filter {
		bsonFilter[k] = v
	}

	var results []*entity.{{.EntityName}}
	err := r.collection.Find(ctx, bsonFilter, &results)
	if err != nil {
		return nil, err
	}

	return results, nil
}

// Save salva um novo {{.EntityName}}
func (r *Mongo{{.EntityName}}Repository) Save(ctx context.Context, e *entity.{{.EntityName}}) error {
	_, err := r.collection.InsertOne(ctx, e)
	return err
}

// Update atualiza um {{.EntityName}} existente
func (r *Mongo{{.EntityName}}Repository) Update(ctx context.Context, e *entity.{{.EntityName}}) error {
	objectID, err := primitive.ObjectIDFromHex(e.ID)
	if err != nil {
		return err
	}

	_, err = r.collection.UpdateOne(ctx, bson.M{"_id": objectID}, bson.M{"$set": e})
	return err
}

// Delete exclui um {{.EntityName}} pelo ID
func (r *Mongo{{.EntityName}}Repository) Delete(ctx context.Context, id string) error {
	objectID, err := primitive.ObjectIDFromHex(id)
	if err != nil {
		return err
	}

	_, err = r.collection.DeleteOne(ctx, bson.M{"_id": objectID})
	return err
}

{{range .CustomMethods}}
// {{.Name}} {{.Description}}
func (r *Mongo{{$.EntityName}}Repository) {{.Name}}({{.Params}}) {{.Returns}} {
	{{.Body}}
}
{{end}}`,
	}
}

// Field representa um campo de uma entidade
type Field struct {
	Name string
	Type string
	Tags string
}

// Method representa um método de uma entidade
type Method struct {
	Name        string
	Description string
	Params      string
	Returns     string
	Body        string
}

// EntitySchema representa o esquema para geração de uma entidade
type EntitySchema struct {
	Name        string
	Description string
	Fields      []Field
	Methods     []Method
}

// RepositorySchema representa o esquema para geração de um repositório
type RepositorySchema struct {
	Name          string
	EntityName    string
	DomainName    string
	CustomMethods []Method
}

// ServiceSchema representa o esquema para geração de um serviço
type ServiceSchema struct {
	Name          string
	EntityName    string
	DomainName    string
	CustomMethods []Method
}

// GenerateEntity gera um arquivo de entidade
func (g *SchemaGenerator) GenerateEntity(schema EntitySchema, outputDir string) error {
	return g.generateFile("entity", schema, outputDir, fmt.Sprintf("%s.go", strings.ToLower(schema.Name)))
}

// GenerateRepository gera um arquivo de repositório
func (g *SchemaGenerator) GenerateRepository(schema RepositorySchema, outputDir string) error {
	return g.generateFile("repository", schema, outputDir, fmt.Sprintf("%s_repository.go", strings.ToLower(schema.EntityName)))
}

// GenerateService gera um arquivo de serviço
func (g *SchemaGenerator) GenerateService(schema ServiceSchema, outputDir string) error {
	return g.generateFile("service", schema, outputDir, fmt.Sprintf("%s_service.go", strings.ToLower(schema.EntityName)))
}

// GenerateMongoRepository gera um arquivo de implementação de repositório MongoDB
func (g *SchemaGenerator) GenerateMongoRepository(schema RepositorySchema, outputDir string) error {
	return g.generateFile("mongo_repository", schema, outputDir, fmt.Sprintf("%s_repository.go", strings.ToLower(schema.EntityName)))
}

// generateFile gera um arquivo a partir de um template e esquema
func (g *SchemaGenerator) generateFile(templateName string, data interface{}, outputDir, fileName string) error {
	// Obter o template
	tmplStr, ok := g.Templates[templateName]
	if !ok {
		return fmt.Errorf("template não encontrado: %s", templateName)
	}

	// Analisar o template
	tmpl, err := template.New(templateName).Parse(tmplStr)
	if err != nil {
		return fmt.Errorf("erro ao analisar template: %v", err)
	}

	// Criar diretório se não existir
	fullOutputDir := filepath.Join(g.BaseDir, outputDir)
	if err := os.MkdirAll(fullOutputDir, 0755); err != nil {
		return fmt.Errorf("erro ao criar diretório: %v", err)
	}

	// Criar o arquivo
	outputPath := filepath.Join(fullOutputDir, fileName)
	file, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("erro ao criar arquivo: %v", err)
	}
	defer file.Close()

	// Executar o template
	if err := tmpl.Execute(file, data); err != nil {
		return fmt.Errorf("erro ao executar template: %v", err)
	}

	return nil
}

// AddTemplate adiciona um novo template ou substitui um existente
func (g *SchemaGenerator) AddTemplate(name, template string) {
	g.Templates[name] = template
}

// RegisterTemplateFromFile carrega um template a partir de um arquivo
func (g *SchemaGenerator) RegisterTemplateFromFile(name, filePath string) error {
	content, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("erro ao ler arquivo de template: %v", err)
	}

	g.Templates[name] = string(content)
	return nil
}

// ProjectGenerator gera a estrutura de um projeto
type ProjectGenerator struct {
	BaseDir   string
	Templates map[string]string
}

// NewProjectGenerator cria um novo gerador de projetos
func NewProjectGenerator(baseDir string) *ProjectGenerator {
	return &ProjectGenerator{
		BaseDir:   baseDir,
		Templates: defaultProjectTemplates(),
	}
}

// defaultProjectTemplates retorna os templates padrão para geração de projetos
func defaultProjectTemplates() map[string]string {
	return map[string]string{
		"main": `package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"{{ .ModulePath }}/config"
)

func main() {
	// Carregar configurações
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Erro ao carregar configurações: %v", err)
	}

	// Configurar servidor HTTP
	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.HTTPPort),
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
		// Configurar handler aqui
	}

	// Iniciar o servidor em uma goroutine separada
	go func() {
		log.Printf("Servidor iniciado na porta %d", cfg.HTTPPort)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Erro ao iniciar servidor: %v", err)
		}
	}()

	// Aguardar sinal para encerramento gracioso
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Encerrando servidor...")

	// Contexto com timeout para encerramento
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Erro ao encerrar servidor: %v", err)
	}

	log.Println("Servidor encerrado com sucesso")
}
`,
		"config": `package config

import (
	"fmt"

	"github.com/spf13/viper"
)

// Config representa a configuração da aplicação
type Config struct {
	// Ambiente
	Environment string

	// HTTP
	HTTPPort int

	// Database
	DatabaseURI  string
	DatabaseName string

	// Kafka
	KafkaBootstrapServers string
	KafkaConsumerGroupID  string

	// Logging
	LogLevel string
}

// Load carrega a configuração a partir de variáveis de ambiente ou arquivo .env
func Load() (*Config, error) {
	v := viper.New()

	// Valores padrão
	v.SetDefault("ENVIRONMENT", "development")
	v.SetDefault("HTTP_PORT", 8080)
	v.SetDefault("LOG_LEVEL", "info")

	// Ler de arquivo .env
	v.SetConfigName(".env")
	v.SetConfigType("env")
	v.AddConfigPath(".")
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
			return nil, fmt.Errorf("erro ao ler arquivo de configuração: %v", err)
		}
	}

	// Ler de variáveis de ambiente
	v.AutomaticEnv()

	// Mapear para estrutura
	config := &Config{
		Environment: v.GetString("ENVIRONMENT"),
		HTTPPort:    v.GetInt("HTTP_PORT"),
		DatabaseURI: v.GetString("DATABASE_URI"),
		DatabaseName: v.GetString("DATABASE_NAME"),
		KafkaBootstrapServers: v.GetString("KAFKA_BOOTSTRAP_SERVERS"),
		KafkaConsumerGroupID: v.GetString("KAFKA_CONSUMER_GROUP_ID"),
		LogLevel: v.GetString("LOG_LEVEL"),
	}

	return config, nil
}
`,
		"go-mod": `module {{ .ModulePath }}

go {{ .GoVersion }}

require (
	github.com/spf13/viper v1.15.0
	github.com/systentandobr/go-commons-toolkit v0.1.0
)
`,
		"makefile": `# Variáveis
BINARY_NAME={{ .ProjectName }}
BUILD_DIR=./build
CONFIG_FILE=.env
GO_FILES=$(shell find . -name "*.go" -not -path "./vendor/*")

# Comando padrão
all: build

# Compilar o binário
build:
	@echo "Compilando o binário..."
	@go build -o $(BUILD_DIR)/$(BINARY_NAME) ./cmd/{{ .ProjectName }}

# Executar a aplicação
run:
	@go run ./cmd/{{ .ProjectName }}

# Executar os testes
test:
	@echo "Executando testes..."
	@go test -v ./...

# Limpar arquivos de build
clean:
	@echo "Limpando arquivos de build..."
	@rm -rf $(BUILD_DIR)

# Construir imagem Docker
docker-build:
	@echo "Construindo imagem Docker..."
	@docker build -t {{ .ProjectName }}:latest .

# Atualizar dependências
deps:
	@echo "Atualizando dependências..."
	@go mod tidy

# Criar arquivo de configuração
config:
	@if [ ! -f $(CONFIG_FILE) ]; then \
		echo "Criando arquivo de configuração $(CONFIG_FILE)..."; \
		cp $(CONFIG_FILE).example $(CONFIG_FILE); \
	else \
		echo "Arquivo de configuração $(CONFIG_FILE) já existe."; \
	fi

# Formatar código
fmt:
	@echo "Formatando código..."
	@gofmt -s -w $(GO_FILES)

# Verificar código
lint:
	@echo "Verificando código..."
	@golangci-lint run

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make build       - Compilar o binário"
	@echo "  make run         - Executar a aplicação"
	@echo "  make test        - Executar os testes"
	@echo "  make clean       - Limpar arquivos de build"
	@echo "  make docker-build- Construir imagem Docker"
	@echo "  make deps        - Atualizar dependências"
	@echo "  make config      - Criar arquivo de configuração"
	@echo "  make fmt         - Formatar código"
	@echo "  make lint        - Verificar código"

.PHONY: all build run test clean docker-build deps config fmt lint help
`,
		"dockerfile": `FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copiar arquivos de dependências
COPY go.mod go.sum ./
RUN go mod download

# Copiar código-fonte
COPY . .

# Compilar a aplicação
RUN CGO_ENABLED=0 GOOS=linux go build -o app ./cmd/{{ .ProjectName }}

# Imagem final
FROM alpine:3.19

WORKDIR /app

# Copiar binário compilado
COPY --from=builder /app/app .
COPY --from=builder /app/.env.example .env

# Configurar usuário não-root
RUN adduser -D appuser
USER appuser

# Expor porta
EXPOSE {{ .Port }}

# Executar a aplicação
CMD ["./app"]
`,
		"gitignore": `# Binaries
/build/
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, build with 'go test -c'
*.test

# Output of the go coverage tool
*.out

# Dependency directories
/vendor/

# Environment variables
.env
.env.*
!.env.example

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Log files
*.log

# Build directories
/dist/
`,
		"readme": `# {{ .ProjectName }}

{{ .Description }}

## Requisitos

- Go {{ .GoVersion }} ou superior
- Docker (opcional)

## Configuração

1. Clone o repositório:
   ` + "```sh" + `
   git clone {{ .RepositoryURL }}
   cd {{ .ProjectName }}
   ` + "```" + `

2. Copie o arquivo de configuração:
   ` + "```sh" + `
   cp .env.example .env
   ` + "```" + `

3. Edite o arquivo ` + "`.env`" + ` conforme necessário.

## Compilação

` + "```sh" + `
make build
` + "```" + `

## Execução

` + "```sh" + `
make run
` + "```" + `

## Testes

` + "```sh" + `
make test
` + "```" + `

## Docker

` + "```sh" + `
make docker-build
docker run -p {{ .Port }}:{{ .Port }} {{ .ProjectName }}:latest
` + "```" + `

## Estrutura do Projeto

` + "```" + `
{{ .ProjectName }}/
├── cmd/{{ .ProjectName }}/     # Ponto de entrada da aplicação
├── config/                     # Configurações da aplicação
├── internal/                   # Código privado
│   ├── domain/                 # Domínio da aplicação
│   ├── application/            # Casos de uso da aplicação
│   ├── infrastructure/         # Adaptadores de infraestrutura
├── pkg/                        # Código público reutilizável
└── test/                       # Testes integrados
` + "```" + `

## Licença

{{ .License }}
`,
		"env-example": `# Ambiente (development, production, test)
ENVIRONMENT=development

# Servidor HTTP
HTTP_PORT={{ .Port }}

# Banco de Dados
DATABASE_URI=mongodb://localhost:27017
DATABASE_NAME={{ .ProjectName }}

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP_ID={{ .ProjectName }}-group

# Logging
LOG_LEVEL=info
`,
		"domain-entity": `package entity

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// {{ .EntityName }} representa {{ .EntityDescription }}
type {{ .EntityName }} struct {
	ID        primitive.ObjectID ` + "`json:\"id\" bson:\"_id,omitempty\"`" + `
	CreatedAt time.Time          ` + "`json:\"created_at\" bson:\"created_at\"`" + `
	UpdatedAt time.Time          ` + "`json:\"updated_at\" bson:\"updated_at\"`" + `
}

// New{{ .EntityName }} cria uma nova instância de {{ .EntityName }}
func New{{ .EntityName }}() *{{ .EntityName }} {
	now := time.Now()
	return &{{ .EntityName }}{
		CreatedAt: now,
		UpdatedAt: now,
	}
}
`,
		"domain-repository": `package repository

import (
	"context"

	"{{ .ModulePath }}/internal/domain/{{ .DomainName }}/entity"
)

// {{ .EntityName }}Repository define as operações para o repositório de {{ .EntityName }}
type {{ .EntityName }}Repository interface {
	FindByID(ctx context.Context, id string) (*entity.{{ .EntityName }}, error)
	FindAll(ctx context.Context) ([]*entity.{{ .EntityName }}, error)
	Save(ctx context.Context, entity *entity.{{ .EntityName }}) error
	Update(ctx context.Context, entity *entity.{{ .EntityName }}) error
	Delete(ctx context.Context, id string) error
}
`,
	}
}

// ProjectConfig representa a configuração para geração de um projeto
type ProjectConfig struct {
	ProjectName       string
	Description       string
	ModulePath        string
	GoVersion         string
	Port              int
	RepositoryURL     string
	License           string
	EntityName        string
	EntityDescription string
	DomainName        string
}

// GenerateProject gera a estrutura básica de um projeto
func (g *ProjectGenerator) GenerateProject(config ProjectConfig) error {
	// Criar diretório base do projeto
	projectDir := filepath.Join(g.BaseDir, config.ProjectName)
	if err := os.MkdirAll(projectDir, 0755); err != nil {
		return fmt.Errorf("erro ao criar diretório do projeto: %v", err)
	}

	// Criar estrutura de diretórios
	dirs := []string{
		"cmd/" + config.ProjectName,
		"config",
		"internal/domain/" + config.DomainName + "/entity",
		"internal/domain/" + config.DomainName + "/repository",
		"internal/domain/" + config.DomainName + "/service",
		"internal/application",
		"internal/infrastructure/persistence",
		"internal/infrastructure/http",
		"pkg",
		"test",
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(filepath.Join(projectDir, dir), 0755); err != nil {
			return fmt.Errorf("erro ao criar diretório %s: %v", dir, err)
		}
	}

	// Criar arquivos a partir dos templates
	files := map[string]string{
		"cmd/" + config.ProjectName + "/main.go": "main",
		"config/config.go":                       "config",
		"go.mod":                                 "go-mod",
		"Makefile":                               "makefile",
		"Dockerfile":                             "dockerfile",
		".gitignore":                             "gitignore",
		"README.md":                              "readme",
		".env.example":                           "env-example",
	}

	// Adicionar entidade e repositório de domínio se especificados
	if config.EntityName != "" && config.DomainName != "" {
		files["internal/domain/"+config.DomainName+"/entity/"+strings.ToLower(config.EntityName)+".go"] = "domain-entity"
		files["internal/domain/"+config.DomainName+"/repository/"+strings.ToLower(config.EntityName)+"_repository.go"] = "domain-repository"
	}

	for file, templateName := range files {
		if err := g.generateProjectFile(config, projectDir, file, templateName); err != nil {
			return fmt.Errorf("erro ao gerar arquivo %s: %v", file, err)
		}
	}

	return nil
}

// generateProjectFile gera um arquivo a partir de um template
func (g *ProjectGenerator) generateProjectFile(config ProjectConfig, projectDir, filePath, templateName string) error {
	// Obter o template
	tmplStr, ok := g.Templates[templateName]
	if !ok {
		return fmt.Errorf("template não encontrado: %s", templateName)
	}

	// Analisar o template
	tmpl, err := template.New(templateName).Parse(tmplStr)
	if err != nil {
		return fmt.Errorf("erro ao analisar template: %v", err)
	}

	// Criar o arquivo
	fullPath := filepath.Join(projectDir, filePath)
	if err := os.MkdirAll(filepath.Dir(fullPath), 0755); err != nil {
		return fmt.Errorf("erro ao criar diretório para arquivo: %v", err)
	}

	file, err := os.Create(fullPath)
	if err != nil {
		return fmt.Errorf("erro ao criar arquivo: %v", err)
	}
	defer file.Close()

	// Executar o template
	if err := tmpl.Execute(file, config); err != nil {
		return fmt.Errorf("erro ao executar template: %v", err)
	}

	return nil
}

// AddProjectTemplate adiciona um novo template ou substitui um existente
func (g *ProjectGenerator) AddProjectTemplate(name, template string) {
	g.Templates[name] = template
}

// CreateMicroservice cria um projeto de microsserviço completo
func (g *ProjectGenerator) CreateMicroservice(config ProjectConfig) error {
	// Configurações padrão se não especificadas
	if config.GoVersion == "" {
		config.GoVersion = "1.21"
	}
	if config.Port == 0 {
		config.Port = 8080
	}
	if config.License == "" {
		config.License = "MIT"
	}

	// Criar o projeto base
	if err := g.GenerateProject(config); err != nil {
		return err
	}

	fmt.Printf("Microsserviço %s criado com sucesso em %s\n", config.ProjectName, filepath.Join(g.BaseDir, config.ProjectName))
	return nil
}

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
	BaseDir string
	Templates map[string]string
}

// NewSchemaGenerator cria um novo gerador de esquemas
func NewSchemaGenerator(baseDir string) *SchemaGenerator {
	return &SchemaGenerator{
		BaseDir: baseDir,
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

package tools

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/persistence/mongodb"
)

// Migration representa uma migração de banco de dados
type Migration struct {
	Version     string    `bson:"version"`
	Description string    `bson:"description"`
	AppliedAt   time.Time `bson:"applied_at"`
}

// DBMigrator gerencia migrações de banco de dados
type DBMigrator struct {
	client         *mongo.Client
	database       *mongo.Database
	collectionName string
	migrationsDir  string
}

// MigrationFunction representa uma função de migração
type MigrationFunction func(context.Context, *mongo.Database) error

// MigrationFile representa um arquivo de migração
type MigrationFile struct {
	Version     string
	Description string
	Path        string
	Up          MigrationFunction
	Down        MigrationFunction
}

// NewDBMigrator cria um novo migrador de banco de dados
func NewDBMigrator(migrationsDir, collectionName string) (*DBMigrator, error) {
	client, err := mongodb.GetClient()
	if err != nil {
		return nil, fmt.Errorf("erro ao conectar ao MongoDB: %v", err)
	}

	db, err := mongodb.GetDatabase()
	if err != nil {
		return nil, fmt.Errorf("erro ao obter banco de dados: %v", err)
	}

	return &DBMigrator{
		client:         client,
		database:       db,
		collectionName: collectionName,
		migrationsDir:  migrationsDir,
	}, nil
}

// Create cria um novo arquivo de migração
func (m *DBMigrator) Create(name string) (string, error) {
	// Criar diretório se não existir
	if err := os.MkdirAll(m.migrationsDir, 0755); err != nil {
		return "", fmt.Errorf("erro ao criar diretório de migrações: %v", err)
	}

	// Gerar versão baseada na data e hora atual
	version := time.Now().UTC().Format("20060102150405")
	
	// Preparar nome do arquivo
	fileName := fmt.Sprintf("%s_%s.go", version, strings.ReplaceAll(strings.ToLower(name), " ", "_"))
	filePath := filepath.Join(m.migrationsDir, fileName)

	// Criar conteúdo da migração
	content := fmt.Sprintf(`package migrations

import (
	"context"
	"fmt"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

// Up%s executa a migração para frente
func Up%s(ctx context.Context, db *mongo.Database) error {
	// Implementar a migração aqui
	fmt.Println("Aplicando migração %s: %s")
	
	// Exemplo:
	// collection := db.Collection("sua_colecao")
	// _, err := collection.InsertOne(ctx, bson.M{"campo": "valor"})
	// return err
	
	return nil
}

// Down%s reverte a migração
func Down%s(ctx context.Context, db *mongo.Database) error {
	// Implementar a reversão da migração aqui
	fmt.Println("Revertendo migração %s: %s")
	
	// Exemplo:
	// collection := db.Collection("sua_colecao")
	// _, err := collection.DeleteOne(ctx, bson.M{"campo": "valor"})
	// return err
	
	return nil
}
`,
		formatFuncName(version, name),
		formatFuncName(version, name),
		version, name,
		formatFuncName(version, name),
		formatFuncName(version, name),
		version, name,
	)

	// Escrever arquivo
	if err := os.WriteFile(filePath, []byte(content), 0644); err != nil {
		return "", fmt.Errorf("erro ao escrever arquivo de migração: %v", err)
	}

	return filePath, nil
}

// formatFuncName formata o nome da função para CamelCase
func formatFuncName(version, name string) string {
	// Remover caracteres não alfanuméricos e converter para CamelCase
	words := strings.Fields(strings.Map(func(r rune) rune {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') {
			return r
		}
		return ' '
	}, name))

	for i, word := range words {
		if i == 0 {
			words[i] = strings.Title(strings.ToLower(word))
		} else {
			words[i] = strings.Title(strings.ToLower(word))
		}
	}

	return version + strings.Join(words, "")
}

// Migrate aplica todas as migrações pendentes
func (m *DBMigrator) Migrate(ctx context.Context, migrations []MigrationFile) error {
	// Obter coleção de migrações
	collection := m.database.Collection(m.collectionName)

	// Verificar migrações já aplicadas
	appliedMigrations := make(map[string]Migration)
	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil && err != mongo.ErrNoDocuments {
		return fmt.Errorf("erro ao consultar migrações aplicadas: %v", err)
	}

	if err != mongo.ErrNoDocuments {
		var results []Migration
		if err := cursor.All(ctx, &results); err != nil {
			return fmt.Errorf("erro ao ler migrações aplicadas: %v", err)
		}

		for _, migration := range results {
			appliedMigrations[migration.Version] = migration
		}
	}

	// Ordenar migrações por versão
	sort.Slice(migrations, func(i, j int) bool {
		return migrations[i].Version < migrations[j].Version
	})

	// Aplicar migrações pendentes
	for _, migration := range migrations {
		if _, applied := appliedMigrations[migration.Version]; !applied {
			fmt.Printf("Aplicando migração %s: %s\n", migration.Version, migration.Description)

			// Executar migração
			if err := migration.Up(ctx, m.database); err != nil {
				return fmt.Errorf("erro ao aplicar migração %s: %v", migration.Version, err)
			}

			// Registrar migração aplicada
			_, err := collection.InsertOne(ctx, Migration{
				Version:     migration.Version,
				Description: migration.Description,
				AppliedAt:   time.Now(),
			})
			if err != nil {
				return fmt.Errorf("erro ao registrar migração %s: %v", migration.Version, err)
			}

			fmt.Printf("Migração %s aplicada com sucesso\n", migration.Version)
		}
	}

	return nil
}

// Rollback reverte a última migração aplicada
func (m *DBMigrator) Rollback(ctx context.Context, migrations []MigrationFile) error {
	// Obter coleção de migrações
	collection := m.database.Collection(m.collectionName)

	// Obter última migração aplicada
	opts := options.FindOne().SetSort(bson.M{"version": -1})
	var lastMigration Migration
	err := collection.FindOne(ctx, bson.M{}, opts).Decode(&lastMigration)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return fmt.Errorf("nenhuma migração para reverter")
		}
		return fmt.Errorf("erro ao consultar última migração: %v", err)
	}

	// Encontrar a função de reversão correspondente
	var downFunc MigrationFunction
	var migrationFile MigrationFile
	found := false

	for _, migration := range migrations {
		if migration.Version == lastMigration.Version {
			downFunc = migration.Down
			migrationFile = migration
			found = true
			break
		}
	}

	if !found || downFunc == nil {
		return fmt.Errorf("função de reversão não encontrada para migração %s", lastMigration.Version)
	}

	// Executar reversão
	fmt.Printf("Revertendo migração %s: %s\n", migrationFile.Version, migrationFile.Description)
	if err := downFunc(ctx, m.database); err != nil {
		return fmt.Errorf("erro ao reverter migração %s: %v", migrationFile.Version, err)
	}

	// Remover registro da migração
	_, err = collection.DeleteOne(ctx, bson.M{"version": lastMigration.Version})
	if err != nil {
		return fmt.Errorf("erro ao remover registro da migração %s: %v", lastMigration.Version, err)
	}

	fmt.Printf("Migração %s revertida com sucesso\n", migrationFile.Version)
	return nil
}

// Status exibe o status das migrações
func (m *DBMigrator) Status(ctx context.Context, migrations []MigrationFile) ([]map[string]interface{}, error) {
	// Obter coleção de migrações
	collection := m.database.Collection(m.collectionName)

	// Verificar migrações já aplicadas
	appliedMigrations := make(map[string]Migration)
	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil && err != mongo.ErrNoDocuments {
		return nil, fmt.Errorf("erro ao consultar migrações aplicadas: %v", err)
	}

	if err != mongo.ErrNoDocuments {
		var results []Migration
		if err := cursor.All(ctx, &results); err != nil {
			return nil, fmt.Errorf("erro ao ler migrações aplicadas: %v", err)
		}

		for _, migration := range results {
			appliedMigrations[migration.Version] = migration
		}
	}

	// Ordenar migrações por versão
	sort.Slice(migrations, func(i, j int) bool {
		return migrations[i].Version < migrations[j].Version
	})

	// Preparar status
	status := make([]map[string]interface{}, len(migrations))
	for i, migration := range migrations {
		applied, isApplied := appliedMigrations[migration.Version]
		
		status[i] = map[string]interface{}{
			"version":     migration.Version,
			"description": migration.Description,
			"status":      isApplied,
		}
		
		if isApplied {
			status[i]["applied_at"] = applied.AppliedAt
		}
	}

	return status, nil
}

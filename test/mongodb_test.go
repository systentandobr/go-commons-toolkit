package test

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/persistence/mongodb"
)

func TestMongoDB(t *testing.T) {

	t.Run("Teste configuração MongoDB", func(t *testing.T) {

		fmt.Println("==== Teste de Configuração e Conexão ====")
		fmt.Println("Validando configurações e testando conexões...")

		config.ValidaCarregarEnvFile(t)

		// Obter configurações
		cfg := config.Get()

		// Exibir configurações básicas
		fmt.Println("\n=== Configurações da Aplicação ===")
		fmt.Printf("Ambiente: %s\n", cfg.Environment)
		fmt.Printf("Porta API: %s\n", cfg.APIPort)
		fmt.Printf("Swagger: %s\n", config.StatusBool(cfg.EnableSwagger))
		fmt.Printf("CORS: %s\n", config.StatusBool(cfg.EnableCORS))
		fmt.Printf("Jobs: %s\n", config.StatusBool(cfg.EnableJobs))
		fmt.Printf("Métricas: %s\n", config.StatusBool(cfg.EnableMetrics))
		fmt.Printf("Tracing: %s\n", config.StatusBool(cfg.EnableTracing))

		// Validar e testar conexão com MongoDB
		testMongoDB(cfg, t)

		fmt.Println("\n==== Teste de Configuração Concluído ====")

	})
}

// testMongoDB valida as configurações e testa a conexão com MongoDB
func testMongoDB(cfg *config.Config, t *testing.T) {
	fmt.Println("\n=== MongoDB ===")

	// Validar configurações
	config.ValidarConfiguracao(cfg.Database.MongoURI, "URI MongoDB", "mongodb://localhost:27017")
	config.ValidarConfiguracao(cfg.Database.MongoDatabaseName, "Nome do Banco MongoDB", "my_database")

	// Tentar conectar ao MongoDB
	fmt.Print("Testando conexão: ")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	client, err := mongodb.GetClient()
	if err != nil {
		const messageError = "❌ Falha ao conectar: %v\n"
		t.Fatalf(messageError, err)
		return
	}

	err = client.Ping(ctx, nil)
	if err != nil {
		const messageError = "❌ Falha ao fazer ping: %v\n"
		t.Fatalf(messageError, err)
	} else {
		fmt.Println("✅ Conectado com sucesso")

		// Testar acesso ao banco de dados
		database, err := mongodb.GetDatabase()
		if err != nil {
			const messageError = "❌ Falha ao acessar o banco de dados: %v\n"
			t.Fatalf(messageError, err)
		} else {
			fmt.Printf("✅ Banco '%s' acessado com sucesso\n", cfg.Database.MongoDatabaseName)
			database.Client().Ping(ctx, nil)
			// Opcionalmente testar uma coleção
			colName := "test_collection"
			col, err := mongodb.NewCollection(colName)
			if err != nil {
				const messageError = "❌ Falha ao acessar coleção: %v\n"
				t.Fatalf(messageError, err)
			} else {
				fmt.Printf("✅ Coleção '%s' acessada com sucesso\n", colName)

				// Contar documentos para verificar comunicação
				count, err := col.CountDocuments(ctx, map[string]interface{}{})
				if err != nil {
					const messageError = "❌ Falha ao contar documentos: %v\n"
					t.Fatalf(messageError, err)
				} else {
					fmt.Printf("✅ Contagem de documentos: %d\n", count)
				}
			}
		}
	}
}

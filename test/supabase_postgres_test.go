package test

import (
	"fmt"
	"testing"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/persistence/supabase"
)

func TestSupabaseDB(t *testing.T) {

	t.Run("Teste configuração PostgreSQL", func(t *testing.T) {
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

		// Validar e testar conexão com Supabase
		testSupabase(cfg)

		fmt.Println("\n==== Teste de Configuração Concluído ====")
	})
}

// testSupabase valida as configurações e testa a conexão com Supabase
func testSupabase(cfg *config.Config) {
	fmt.Println("\n=== Supabase/PostgreSQL ===")

	// Validar configurações
	config.ValidarConfiguracao(cfg.Database.SupabaseURI, "URI Supabase", "postgresql://localhost:5432")
	config.ValidarConfiguracao(cfg.Database.SupabaseDatabase, "Nome do Banco", "postgres")
	config.ValidarConfiguracao(cfg.Database.SupabaseUsername, "Usuário", "postgres")

	// Não exibimos a senha por segurança
	if cfg.Database.SupabasePassword == "postgres" || cfg.Database.SupabasePassword == "" {
		fmt.Printf("%-25s: %s %s\n", "Senha", config.StatusMissing, "(valor padrão)")
	} else {
		fmt.Printf("%-25s: %s %s\n", "Senha", config.StatusOK, "*****")
	}

	// Tentar conectar ao Supabase
	fmt.Print("Testando conexão: ")

	dbClient, err := supabase.GetClient()
	if err != nil {
		fmt.Printf("❌ Falha ao conectar: %v\n", err)
		return
	}

	fmt.Printf("dbClient inUse:: %v\n", dbClient.Stats().InUse)
	fmt.Printf("dbClient OpenConnections:: %v\n", dbClient.Stats().OpenConnections)

	err = dbClient.Ping()
	if err != nil {
		fmt.Printf("❌ Falha ao fazer ping: %v\n", err)
	} else {
		fmt.Println("✅ Conectado com sucesso")

		// Testar uma consulta básica
		var version string
		err = dbClient.QueryRow("SELECT version()").Scan(&version)
		if err != nil {
			fmt.Printf("❌ Falha ao executar consulta: %v\n", err)
		} else {
			fmt.Printf("✅ Consulta executada com sucesso\n")
			fmt.Printf("  Versão PostgreSQL: %s\n", version)
		}
	}

	// Fechar conexão após o teste
	if dbClient != nil {
		_ = dbClient.Close()
		dbClient = nil
		fmt.Printf("✅ Conexão fechada executada com sucesso\n")
	}
}

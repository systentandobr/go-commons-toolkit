package main

import (
	"database/sql"
	"fmt"
	"net"
	"time"

	_ "github.com/lib/pq" // PostgreSQL driver
	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
)

func main() {
	// Carregar configuração
	config.LoadEnv(".env.fixed")
	cfg := config.Get()

	fmt.Println("=== Teste de conexão com PostgreSQL ===")

	// Mostrar configurações
	fmt.Println("Configuração atual:")
	fmt.Printf("URI: %s\n", cfg.Database.SupabaseURI)
	fmt.Printf("Database: %s\n", cfg.Database.SupabaseDatabase)
	fmt.Printf("Username: %s\n", cfg.Database.SupabaseUsername)
	fmt.Printf("Password: %s\n", maskPassword(cfg.Database.SupabasePassword))

	// Testar conexão TCP com diferentes hosts
	fmt.Println("\nTestes de conectividade TCP:")
	hosts := []string{"localhost", "127.0.0.1", "0.0.0.0"}
	port := "5432"

	for _, host := range hosts {
		testTCPConnection(host, port)
	}

	// Tentar conexão SQL com os mesmos hosts
	fmt.Println("\nTestes de conexão SQL:")
	for _, host := range hosts {
		testSQLConnection(
			host,
			port,
			cfg.Database.SupabaseDatabase,
			cfg.Database.SupabaseUsername,
			cfg.Database.SupabasePassword,
		)
	}

	fmt.Println("\nSoluções possíveis:")
	fmt.Println("1. Verifique se o container do PostgreSQL está em execução:")
	fmt.Println("   docker ps | grep postgres")

	fmt.Println("\n2. Verifique o mapeamento de portas:")
	fmt.Println("   docker-compose ps postgres")

	fmt.Println("\n3. Teste a conexão diretamente via psql:")
	fmt.Println("   psql -h 127.0.0.1 -p 5432 -U postgres")

	fmt.Println("\n4. Experimente alterar a configuração para usar '127.0.0.1' em vez de 'localhost'")
	fmt.Println("   Edite .env: SUPABASE_URI=postgresql://127.0.0.1:5432")

	fmt.Println("\n5. Verifique as configurações de rede do Docker:")
	fmt.Println("   docker network inspect toolkit-network")
}

// Testa a conexão TCP com o host e porta especificados
func testTCPConnection(host, port string) {
	addr := net.JoinHostPort(host, port)
	fmt.Printf("Testando TCP %s: ", addr)

	conn, err := net.DialTimeout("tcp", addr, 2*time.Second)
	if err != nil {
		fmt.Printf("❌ Falha: %v\n", err)
		return
	}
	defer conn.Close()

	fmt.Println("✅ Conectado")
}

// Testa a conexão SQL completa
func testSQLConnection(host, port, dbname, user, password string) {
	connStr := fmt.Sprintf(
		"host=%s port=%s dbname=%s user=%s password=%s sslmode=disable",
		host, port, dbname, user, password,
	)

	fmt.Printf("Testando SQL %s:%s: ", host, port)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		fmt.Printf("❌ Falha ao abrir: %v\n", err)
		return
	}
	defer db.Close()

	// Definir timeout curto
	db.SetConnMaxLifetime(5 * time.Second)

	err = db.Ping()
	if err != nil {
		fmt.Printf("❌ Falha no ping: %v\n", err)
		return
	}

	// Testar uma consulta simples
	var version string
	err = db.QueryRow("SELECT version()").Scan(&version)
	if err != nil {
		fmt.Printf("✅ Conectado, mas falha na consulta: %v\n", err)
		return
	}

	fmt.Printf("✅ Conectado: %s\n", version[:30]+"...")
}

// Oculta a senha para exibição
func maskPassword(password string) string {
	if len(password) <= 2 {
		return "***"
	}
	return password[:1] + "****"
}

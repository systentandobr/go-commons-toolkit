package main

import (
	"database/sql"
	"fmt"
	"net"
	"strings"
	"sync"

	_ "github.com/lib/pq" // Driver PostgreSQL
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
)

var (
	dbInstance *sql.DB
	dbOnce     sync.Once
	dbError    error
)

// GetClient retorna uma instância compartilhada do cliente PostgreSQL
func GetClient() (*sql.DB, error) {
	dbOnce.Do(func() {
		cfg := config.Get()

		// Extrai host e porta da URI
		host, port := extractHostPort(cfg.Database.SupabaseURI)

		// Montando a string de conexão PostgreSQL
		connStr := fmt.Sprintf(
			"host=%s port=%s dbname=%s user=%s password=%s sslmode=disable",
			host,
			port,
			cfg.Database.SupabaseDatabase,
			cfg.Database.SupabaseUsername,
			cfg.Database.SupabasePassword,
		)

		dbInstance, dbError = sql.Open("postgres", connStr)
		if dbError != nil {
			return
		}

		// Verifica se a conexão está ativa
		dbError = dbInstance.Ping()
	})

	return dbInstance, dbError
}

// Extrai o host e porta da URI do PostgreSQL
func extractHostPort(uri string) (string, string) {
	// URI esperada é algo como "postgresql://localhost:5432"
	defaultHost := "127.0.0.1" // Usando IP em vez de hostname
	defaultPort := "5432"

	// Se a URI estiver vazia, retornar valores padrão
	if uri == "" {
		return defaultHost, defaultPort
	}

	// Remover o protocolo (postgresql://)
	uri = strings.TrimPrefix(uri, "postgresql://")

	// Dividir host e porta
	hostPort := strings.Split(uri, ":")

	// Se só tiver host sem porta
	if len(hostPort) == 1 {
		if hostPort[0] == "localhost" {
			return defaultHost, defaultPort
		}
		return hostPort[0], defaultPort
	}

	// Se tiver host e porta
	if hostPort[0] == "localhost" {
		return defaultHost, hostPort[1]
	}

	return hostPort[0], hostPort[1]
}

// Query executa uma consulta SQL e retorna as linhas
func Query(query string, args ...interface{}) (*sql.Rows, error) {
	db, err := GetClient()
	if err != nil {
		return nil, err
	}

	return db.Query(query, args...)
}

// QueryRow executa uma consulta SQL e retorna uma única linha
func QueryRow(query string, args ...interface{}) *sql.Row {
	db, err := GetClient()
	if err != nil {
		return nil
	}

	return db.QueryRow(query, args...)
}

// Exec executa uma declaração SQL sem retornar linhas
func Exec(query string, args ...interface{}) (sql.Result, error) {
	db, err := GetClient()
	if err != nil {
		return nil, err
	}

	return db.Exec(query, args...)
}

// BeginTx inicia uma transação
func BeginTx() (*sql.Tx, error) {
	db, err := GetClient()
	if err != nil {
		return nil, err
	}

	return db.Begin()
}

// Close fecha a conexão com o banco de dados
func Close() error {
	if dbInstance == nil {
		return nil
	}

	return dbInstance.Close()
}

// TestConnection testa a conexão com o PostgreSQL usando os parâmetros fornecidos
func TestConnection(host, port, dbname, user, password string) error {
	connStr := fmt.Sprintf(
		"host=%s port=%s dbname=%s user=%s password=%s sslmode=disable",
		host, port, dbname, user, password,
	)

	fmt.Printf("Testando conexão com: %s\n", connStr)

	// Testar conexão TCP antes de tentar SQL
	addr := net.JoinHostPort(host, port)
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return fmt.Errorf("falha na conexão TCP com %s: %v", addr, err)
	}
	conn.Close()

	// Testar conexão SQL
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return fmt.Errorf("falha ao abrir conexão SQL: %v", err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		return fmt.Errorf("falha no ping SQL: %v", err)
	}

	return nil
}

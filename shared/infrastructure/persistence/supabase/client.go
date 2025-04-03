package supabase

import (
	"database/sql"
	"fmt"
	"sync"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	_ "github.com/lib/pq" // Driver PostgreSQL
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

		// Montando a string de conexão PostgreSQL
		connStr := fmt.Sprintf(
			"host=%s dbname=%s user=%s password=%s sslmode=disable",
			getHost(cfg.SupabaseURI),
			cfg.SupabaseDatabase,
			cfg.SupabaseUsername,
			cfg.SupabasePassword,
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

// Extrai o host da URI do Supabase
func getHost(uri string) string {
	// Implementação simples, pode ser melhorada para casos mais complexos
	// A URI esperada é algo como "postgresql://localhost:5432"
	// Retorna apenas a parte do host (sem o protocolo)
	if len(uri) > 13 {
		return uri[13:]
	}
	return "localhost:5432"
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

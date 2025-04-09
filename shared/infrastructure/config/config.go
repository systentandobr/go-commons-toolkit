package config

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/joho/godotenv"
)

var (
	once     sync.Once
	instance *Config
)

// DatabaseConfig representa as configurações do banco de dados
type DatabaseConfig struct {
	// MongoDB
	MongoURI          string
	MongoDatabaseName string

	// Supabase/PostgreSQL
	SupabaseURI      string
	SupabaseDatabase string
	SupabaseUsername string
	SupabasePassword string
}

// Config representa as configurações da aplicação baseadas em variáveis de ambiente
type Config struct {
	// App
	Environment   string
	APIPort       string
	EnableSwagger bool
	EnableCORS    bool
	EnableJobs    bool
	EnableMetrics bool
	EnableTracing bool

	// Database
	Database DatabaseConfig

	// Kafka
	KafkaBootstrapServer  string
	KafkaConsumerGroupID  string
	KafkaAutoOffsetReset  string
	KafkaEnableAutoCommit bool

	// HTTP
	HTTPPort int
	Timeout  time.Duration
}

// AppConfig é um alias para Config para compatibilidade com o formato solicitado
type AppConfig Config

// LoadEnv carrega as variáveis de ambiente a partir de um arquivo .env
func LoadEnv(filePath string) error {
	return godotenv.Load(filePath)
}

// Get retorna a instância única de configuração (padrão Singleton)
func Get() *Config {
	once.Do(func() {
		instance = &Config{
			// App
			Environment:   getEnv("APP_ENVIRONMENT", "development"),
			APIPort:       getEnv("API_PORT", "8080"),
			EnableSwagger: getBoolEnv("ENABLE_SWAGGER", true),
			EnableCORS:    getBoolEnv("ENABLE_CORS", true),
			EnableJobs:    getBoolEnv("ENABLE_JOBS", true),
			EnableMetrics: getBoolEnv("ENABLE_METRICS", true),
			EnableTracing: getBoolEnv("ENABLE_TRACING", true),

			// Database
			Database: DatabaseConfig{
				// MongoDB
				MongoURI:          getEnv("MONGO_URI", "mongodb://localhost:27017"),
				MongoDatabaseName: getEnv("MONGO_DATABASE_NAME", "my_database"),

				// Supabase/PostgreSQL
				SupabaseURI:      getEnv("SUPABASE_URI", "postgresql://localhost:5432"),
				SupabaseDatabase: getEnv("SUPABASE_DATABASE", "postgres"),
				SupabaseUsername: getEnv("SUPABASE_USERNAME", "postgres"),
				SupabasePassword: getEnv("SUPABASE_PASSWORD", "postgres"),
			},

			// Kafka
			KafkaBootstrapServer:  getEnv("KAFKA_BOOTSTRAP_SERVER", "localhost:9092"),
			KafkaConsumerGroupID:  getEnv("KAFKA_CONSUMER_GROUP_ID", "my-consumer-group"),
			KafkaAutoOffsetReset:  getEnv("KAFKA_AUTO_OFFSET_RESET", "earliest"),
			KafkaEnableAutoCommit: getBoolEnv("KAFKA_ENABLE_AUTO_COMMIT", true),

			// HTTP
			HTTPPort: getIntEnv("HTTP_PORT", 8080),
			Timeout:  time.Duration(getIntEnv("TIMEOUT_SECONDS", 30)) * time.Second,
		}

		validaCarregarEnvFile(nil)
		// Exibir configurações básicas
		validarConfiguracao(nil, nil, nil)
	})

	return instance
}

// getEnv obtém uma variável de ambiente ou retorna o valor padrão
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// getBoolEnv obtém uma variável de ambiente como booleano ou retorna o valor padrão
func getBoolEnv(key string, defaultValue bool) bool {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}

	value, err := strconv.ParseBool(valueStr)
	if err != nil {
		return defaultValue
	}

	return value
}

// Constantes para indicar status da configuração
const (
	StatusOK      = "✅ Configurado"
	StatusMissing = "❌ Não configurado"
)

func validaCarregarEnvFile(t *testing.T) string {
	// Carregar configurações de arquivo .env se existir
	envFile := ".env.example"
	if _, err := os.Stat(envFile); err == nil {
		if err := LoadEnv(envFile); err != nil {
			const messageError = "Aviso: Não foi possível carregar o arquivo .env: %v\n"
			t.Fatalf(messageError, err)
		} else {
			fmt.Println("Arquivo .env carregado com sucesso.")
		}
	} else {
		const messageError = "Arquivo .env não encontrado, usando variáveis de ambiente do sistema."
		t.Error(messageError)
	}
	return "Arquivo .env carregado com sucesso."
}

// statusBool retorna emoji conforme status
func statusBool(enabled bool) string {
	if enabled {
		return StatusOK
	}
	return StatusMissing
}

// validarConfiguracao verifica se uma string de configuração foi definida
func validarConfiguracao(valor, descricao string, padrao string) (string, string) {
	status := StatusOK
	valorExibir := valor

	if valor == padrao || valor == "" {
		status = StatusMissing
		valorExibir = "(valor padrão)"
	}

	fmt.Printf("%-25s: %s %s\n", descricao, status, valorExibir)
	return status, valorExibir
}

// getIntEnv obtém uma variável de ambiente como inteiro ou retorna o valor padrão
func getIntEnv(key string, defaultValue int) int {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}

	value, err := strconv.Atoi(valueStr)
	if err != nil {
		return defaultValue
	}

	return value
}

// getStringSliceEnv obtém uma variável de ambiente como slice de strings (separadas por vírgula)
// GetAppConfig retorna a configuração no formato AppConfig
func GetAppConfig() *AppConfig {
	config := Get()
	appConfig := AppConfig(*config)
	return &appConfig
}

func getStringSliceEnv(key string, defaultValue []string) []string {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}

	return strings.Split(valueStr, ",")
}

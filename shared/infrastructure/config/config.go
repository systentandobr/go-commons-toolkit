package config

import (
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/joho/godotenv"
)

var (
	once     sync.Once
	instance *Config
)

// Config representa as configurações da aplicação baseadas em variáveis de ambiente
type Config struct {
	// MongoDB
	MongoURI          string
	MongoDatabaseName string

	// Kafka
	KafkaBootstrapServer  string
	KafkaConsumerGroupID  string
	KafkaAutoOffsetReset  string
	KafkaEnableAutoCommit bool

	// Supabase/PostgreSQL
	SupabaseURI      string
	SupabaseDatabase string
	SupabaseUsername string
	SupabasePassword string

	// HTTP
	HTTPPort int
	Timeout  time.Duration
}

// LoadEnv carrega as variáveis de ambiente a partir de um arquivo .env
func LoadEnv(filePath string) error {
	return godotenv.Load(filePath)
}

// Get retorna a instância única de configuração (padrão Singleton)
func Get() *Config {
	once.Do(func() {
		instance = &Config{
			// MongoDB
			MongoURI:          getEnv("MONGO_URI", "mongodb://localhost:27017"),
			MongoDatabaseName: getEnv("MONGO_DATABASE_NAME", "my_database"),

			// Kafka
			KafkaBootstrapServer:  getEnv("KAFKA_BOOTSTRAP_SERVER", "localhost:9092"),
			KafkaConsumerGroupID:  getEnv("KAFKA_CONSUMER_GROUP_ID", "my-consumer-group"),
			KafkaAutoOffsetReset:  getEnv("KAFKA_AUTO_OFFSET_RESET", "earliest"),
			KafkaEnableAutoCommit: getBoolEnv("KAFKA_ENABLE_AUTO_COMMIT", true),

			// Supabase/PostgreSQL
			SupabaseURI:      getEnv("SUPABASE_URI", "postgresql://localhost:5432"),
			SupabaseDatabase: getEnv("SUPABASE_DATABASE", "postgres"),
			SupabaseUsername: getEnv("SUPABASE_USERNAME", "postgres"),
			SupabasePassword: getEnv("SUPABASE_PASSWORD", "postgres"),

			// HTTP
			HTTPPort: getIntEnv("HTTP_PORT", 8080),
			Timeout:  time.Duration(getIntEnv("TIMEOUT_SECONDS", 30)) * time.Second,
		}
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
func getStringSliceEnv(key string, defaultValue []string) []string {
	valueStr := os.Getenv(key)
	if valueStr == "" {
		return defaultValue
	}

	return strings.Split(valueStr, ",")
}

package test

import (
	"fmt"
	"testing"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/messaging/kafka"
)

func TestKafkaProducer(t *testing.T) {

	t.Run("Teste configuração Kafka Producer", func(t *testing.T) {
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

		// Validar configuração do Kafka
		testKafka(cfg)

		fmt.Println("\n==== Teste de Configuração Concluído ====")
	})
}

// testKafka valida as configurações do Kafka
func testKafka(cfg *config.Config) {
	fmt.Println("\n=== Kafka ===")

	// Validar configurações
	config.ValidarConfiguracao(cfg.KafkaBootstrapServer, "Bootstrap Server", "localhost:9092")
	config.ValidarConfiguracao(cfg.KafkaConsumerGroupID, "Consumer Group ID", "my-consumer-group")
	config.ValidarConfiguracao(cfg.KafkaAutoOffsetReset, "Auto Offset Reset", "earliest")

	fmt.Printf("%-25s: %s %v\n", "Auto Commit", config.StatusBool(cfg.KafkaEnableAutoCommit), "")

	// Tentar criar um producer de teste (sem enviar mensagens)
	fmt.Print("Tentando criar produtor: ")

	// Tópico de teste
	topicProducer := "test-topic-producer"
	producer := kafka.NewProducer(topicProducer)

	if producer == nil {
		fmt.Printf("❌ Falha ao criar produtor para o tópico %s\n", topicProducer)
	} else {
		fmt.Printf("✅ Produtor criado com sucesso para o tópico %s\n", topicProducer)

		// Fechar o produtor após o teste
		if producer != nil {
			producer.Close()
		}
	}

	// Tentar criar um consumer de teste
	fmt.Print("Tentando criar consumidor: ")

	// Tópico de teste
	topicConsumer := "test-topic-consumer"
	consumer := kafka.NewConsumer(topicConsumer)

	if consumer == nil {
		fmt.Printf("❌ Falha ao criar consumidor para o tópico %s\n", topicConsumer)
	} else {
		fmt.Printf("✅ Consumidor criado com sucesso para o tópico %s\n", topicConsumer)
		// Fechamos o consumidor após o teste para evitar vazamento de recursos
		if consumer != nil {
			consumer.Close()
		}
	}
}

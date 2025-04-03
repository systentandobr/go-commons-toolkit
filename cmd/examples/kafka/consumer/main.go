package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	k "github.com/systentandobr/go-commons-toolkit/shared/infrastructure/messaging/kafka"
)

// Message representa uma mensagem recebida do Kafka
type Message struct {
	ID        string    `json:"id"`
	Content   string    `json:"content"`
	Type      string    `json:"type"`
	CreatedAt time.Time `json:"created_at"`
}

func main() {
	// Carregar configurações
	if err := config.LoadEnv("../../../.env"); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	// Criar um consumidor Kafka
	topic := "example-topic"
	consumer := k.NewConsumer(topic)
	defer consumer.Close()

	// Criar contexto com cancelamento
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Capturar sinais para finalização graciosa
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)

	go func() {
		<-signals
		fmt.Println("Recebido sinal para encerrar. Finalizando...")
		cancel()
	}()

	// Processar mensagens
	fmt.Printf("Consumidor iniciado. Aguardando mensagens do tópico '%s'...\n", topic)
	
	// Definir o handler de mensagens
	handler := func(ctx context.Context, message kafka.Message) error {
		// Desserializar a mensagem
		var msg Message
		if err := json.Unmarshal(message.Value, &msg); err != nil {
			log.Printf("Erro ao desserializar mensagem: %v", err)
			return err
		}

		// Processar a mensagem
		fmt.Printf("Mensagem recebida: ID=%s, Conteúdo=%s, Tipo=%s, Criada em=%v\n",
			msg.ID, msg.Content, msg.Type, msg.CreatedAt)

		return nil
	}

	// Iniciar o consumo de mensagens
	if err := consumer.Consume(ctx, handler); err != nil {
		if err == context.Canceled {
			fmt.Println("Consumidor finalizado.")
		} else {
			log.Fatalf("Erro ao consumir mensagens: %v", err)
		}
	}
}

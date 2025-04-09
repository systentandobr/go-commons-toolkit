package kafkaProducer

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"time"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/messaging/kafka"
)

// Message representa uma mensagem a ser enviada para o Kafka
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

	// Criar um produtor Kafka
	topic := "example-topic"
	producer := kafka.NewProducer(topic)
	defer producer.Close()

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

	// Enviar mensagens periodicamente
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	count := 0
	for {
		select {
		case <-ctx.Done():
			fmt.Println("Produtor finalizado.")
			return
		case <-ticker.C:
			count++
			msg := Message{
				ID:        fmt.Sprintf("msg-%d", count),
				Content:   fmt.Sprintf("Esta é a mensagem %d", count),
				Type:      "example",
				CreatedAt: time.Now(),
			}

			// Converter a mensagem para JSON
			jsonData, err := json.Marshal(msg)
			if err != nil {
				log.Printf("Erro ao serializar mensagem: %v", err)
				continue
			}

			// Enviar a mensagem para o Kafka
			err = producer.Produce(ctx, []byte(msg.ID), jsonData)
			if err != nil {
				log.Printf("Erro ao enviar mensagem: %v", err)
				continue
			}

			fmt.Printf("Mensagem enviada: %s\n", msg.ID)
		}
	}
}

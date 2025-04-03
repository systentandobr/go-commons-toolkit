package kafka

import (
	"context"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
)

// MessageHandler é uma função que processa mensagens Kafka
type MessageHandler func(ctx context.Context, message kafka.Message) error

// Consumer é um consumidor Kafka
type Consumer struct {
	reader *kafka.Reader
	topic  string
}

// NewConsumer cria um novo consumidor Kafka
func NewConsumer(topic string) *Consumer {
	cfg := config.Get()

	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:         []string{cfg.KafkaBootstrapServer},
		Topic:           topic,
		GroupID:         cfg.KafkaConsumerGroupID,
		MinBytes:        10e3, // 10KB
		MaxBytes:        10e6, // 10MB
		MaxWait:         1 * time.Second,
		ReadLagInterval: -1,
		// Pode adicionar mais configurações conforme necessário
	})

	return &Consumer{
		reader: reader,
		topic:  topic,
	}
}

// Consume consome mensagens do tópico Kafka
func (c *Consumer) Consume(ctx context.Context, handler MessageHandler) error {
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			message, err := c.reader.ReadMessage(ctx)
			if err != nil {
				return err
			}

			if err := handler(ctx, message); err != nil {
				return err
			}
		}
	}
}

// Close fecha o consumidor Kafka
func (c *Consumer) Close() error {
	return c.reader.Close()
}

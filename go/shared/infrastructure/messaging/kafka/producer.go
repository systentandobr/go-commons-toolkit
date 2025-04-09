package kafka

import (
	"context"
	"time"

	"github.com/segmentio/kafka-go"
	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
)

// Producer é um produtor Kafka
type Producer struct {
	writer *kafka.Writer
	topic  string
}

// NewProducer cria um novo produtor Kafka
func NewProducer(topic string) *Producer {
	cfg := config.Get()

	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers:      []string{cfg.KafkaBootstrapServer},
		Topic:        topic,
		Balancer:     &kafka.LeastBytes{},
		BatchTimeout: 10 * time.Millisecond,
		// Pode adicionar mais configurações conforme necessário
	})

	return &Producer{
		writer: writer,
		topic:  topic,
	}
}

// Produce envia uma mensagem para o tópico Kafka
func (p *Producer) Produce(ctx context.Context, key, value []byte) error {
	message := kafka.Message{
		Key:   key,
		Value: value,
		Time:  time.Now(),
	}

	return p.writer.WriteMessages(ctx, message)
}

// ProduceMessages envia várias mensagens para o tópico Kafka
func (p *Producer) ProduceMessages(ctx context.Context, messages []kafka.Message) error {
	return p.writer.WriteMessages(ctx, messages...)
}

// Close fecha o produtor Kafka
func (p *Producer) Close() error {
	return p.writer.Close()
}

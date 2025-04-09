package mongodb

import (
	"context"
	"sync"
	"time"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

var (
	clientInstance *mongo.Client
	clientOnce     sync.Once
	clientError    error
)

// GetClient retorna uma instância compartilhada do cliente MongoDB
func GetClient() (*mongo.Client, error) {
	clientOnce.Do(func() {
		cfg := config.Get()

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		clientOptions := options.Client().ApplyURI(cfg.Database.MongoURI)
		clientInstance, clientError = mongo.Connect(ctx, clientOptions)
		if clientError != nil {
			return
		}

		clientError = clientInstance.Ping(ctx, readpref.Primary())
	})

	return clientInstance, clientError
}

// GetDatabase retorna uma instância do banco de dados MongoDB
func GetDatabase() (*mongo.Database, error) {
	cfg := config.Get()
	client, err := GetClient()
	if err != nil {
		return nil, err
	}

	return client.Database(cfg.Database.MongoDatabaseName), nil
}

// Collection representa um wrapper para a coleção MongoDB
type Collection struct {
	collection *mongo.Collection
}

// NewCollection cria um novo wrapper para uma coleção MongoDB
func NewCollection(collectionName string) (*Collection, error) {
	db, err := GetDatabase()
	if err != nil {
		return nil, err
	}

	return &Collection{
		collection: db.Collection(collectionName),
	}, nil
}

// FindOne busca um documento na coleção
func (c *Collection) FindOne(ctx context.Context, filter interface{}, result interface{}) error {
	return c.collection.FindOne(ctx, filter).Decode(result)
}

// Find busca documentos na coleção
func (c *Collection) Find(ctx context.Context, filter interface{}, results interface{}, opts ...*options.FindOptions) error {
	cursor, err := c.collection.Find(ctx, filter, opts...)
	if err != nil {
		return err
	}
	defer cursor.Close(ctx)

	return cursor.All(ctx, results)
}

// InsertOne insere um documento na coleção
func (c *Collection) InsertOne(ctx context.Context, document interface{}) (*mongo.InsertOneResult, error) {
	return c.collection.InsertOne(ctx, document)
}

// InsertMany insere vários documentos na coleção
func (c *Collection) InsertMany(ctx context.Context, documents []interface{}) (*mongo.InsertManyResult, error) {
	return c.collection.InsertMany(ctx, documents)
}

// UpdateOne atualiza um documento na coleção
func (c *Collection) UpdateOne(ctx context.Context, filter interface{}, update interface{}) (*mongo.UpdateResult, error) {
	return c.collection.UpdateOne(ctx, filter, update)
}

// UpdateMany atualiza vários documentos na coleção
func (c *Collection) UpdateMany(ctx context.Context, filter interface{}, update interface{}) (*mongo.UpdateResult, error) {
	return c.collection.UpdateMany(ctx, filter, update)
}

// DeleteOne exclui um documento da coleção
func (c *Collection) DeleteOne(ctx context.Context, filter interface{}) (*mongo.DeleteResult, error) {
	return c.collection.DeleteOne(ctx, filter)
}

// DeleteMany exclui vários documentos da coleção
func (c *Collection) DeleteMany(ctx context.Context, filter interface{}) (*mongo.DeleteResult, error) {
	return c.collection.DeleteMany(ctx, filter)
}

// CountDocuments conta documentos na coleção
func (c *Collection) CountDocuments(ctx context.Context, filter interface{}) (int64, error) {
	return c.collection.CountDocuments(ctx, filter)
}

// Disconnect fecha a conexão com o MongoDB
func Disconnect() error {
	if clientInstance == nil {
		return nil
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	return clientInstance.Disconnect(ctx)
}

package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/persistence/mongodb"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

// User representa um modelo de usuário
type User struct {
	ID        primitive.ObjectID `bson:"_id,omitempty" json:"id"`
	Name      string             `bson:"name" json:"name"`
	Email     string             `bson:"email" json:"email"`
	Password  string             `bson:"password" json:"password,omitempty"`
	CreatedAt time.Time          `bson:"created_at" json:"created_at"`
	UpdatedAt time.Time          `bson:"updated_at" json:"updated_at"`
}

func main() {
	// Carregar configurações
	if err := config.LoadEnv("../../.env"); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	// Criar contexto com timeout
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Criar coleção de usuários
	userCollection, err := mongodb.NewCollection("users")
	if err != nil {
		log.Fatalf("Failed to get users collection: %v", err)
	}

	// Criar um usuário
	user := User{
		Name:      "John Doe",
		Email:     "john@example.com",
		Password:  "hashed_password",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Inserir o usuário
	result, err := userCollection.InsertOne(ctx, user)
	if err != nil {
		log.Fatalf("Failed to insert user: %v", err)
	}

	fmt.Printf("User inserted with ID: %v\n", result.InsertedID)

	// Buscar o usuário pelo email
	var foundUser User
	filter := bson.M{"email": "john@example.com"}
	err = userCollection.FindOne(ctx, filter, &foundUser)
	if err != nil {
		log.Fatalf("Failed to find user: %v", err)
	}

	fmt.Printf("Found user: %+v\n", foundUser)

	// Atualizar o usuário
	update := bson.M{
		"$set": bson.M{
			"name":       "John Updated",
			"updated_at": time.Now(),
		},
	}
	updateResult, err := userCollection.UpdateOne(ctx, bson.M{"_id": foundUser.ID}, update)
	if err != nil {
		log.Fatalf("Failed to update user: %v", err)
	}

	fmt.Printf("Updated %d user(s)\n", updateResult.ModifiedCount)

	// Buscar todos os usuários
	var users []User
	err = userCollection.Find(ctx, bson.M{}, &users)
	if err != nil {
		log.Fatalf("Failed to find users: %v", err)
	}

	fmt.Printf("Found %d user(s)\n", len(users))
	for i, u := range users {
		fmt.Printf("%d. %s (%s)\n", i+1, u.Name, u.Email)
	}

	// Excluir o usuário
	deleteResult, err := userCollection.DeleteOne(ctx, bson.M{"_id": foundUser.ID})
	if err != nil {
		log.Fatalf("Failed to delete user: %v", err)
	}

	fmt.Printf("Deleted %d user(s)\n", deleteResult.DeletedCount)

	// Desconectar do MongoDB
	if err := mongodb.Disconnect(); err != nil {
		log.Printf("Error disconnecting from MongoDB: %v", err)
	}
}

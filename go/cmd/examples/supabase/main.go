package main

import (
	"fmt"
	"log"
	"time"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
	"github.com/systentandobr/toolkit/go/shared/infrastructure/persistence/supabase"
)

// User representa um modelo de usuário
type User struct {
	ID        int64     `json:"id"`
	Name      string    `json:"name"`
	Email     string    `json:"email"`
	Password  string    `json:"password,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

func main() {
	// Carregar configurações
	if err := config.LoadEnv("../../.env"); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	// Obter cliente PostgreSQL
	db, err := supabase.GetClient()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer supabase.Close()

	// Verificar a conexão
	if err := db.Ping(); err != nil {
		log.Fatalf("Failed to ping database: %v", err)
	}

	// Criar tabela de usuários (se não existir)
	_, err = supabase.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			name VARCHAR(100) NOT NULL,
			email VARCHAR(100) UNIQUE NOT NULL,
			password VARCHAR(255) NOT NULL,
			created_at TIMESTAMP NOT NULL DEFAULT NOW(),
			updated_at TIMESTAMP NOT NULL DEFAULT NOW()
		)
	`)
	if err != nil {
		log.Fatalf("Failed to create users table: %v", err)
	}

	// Iniciar uma transação
	tx, err := supabase.BeginTx()
	if err != nil {
		log.Fatalf("Failed to begin transaction: %v", err)
	}

	// Função para reverter a transação em caso de erro
	rollback := func() {
		if err := tx.Rollback(); err != nil {
			log.Printf("Error rolling back transaction: %v", err)
		}
	}

	// Inserir um usuário
	var userID int64
	err = tx.QueryRow(`
		INSERT INTO users (name, email, password, created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5)
		RETURNING id
	`, "Jane Doe", "jane@example.com", "hashed_password", time.Now(), time.Now()).Scan(&userID)
	if err != nil {
		rollback()
		log.Fatalf("Failed to insert user: %v", err)
	}

	fmt.Printf("User inserted with ID: %d\n", userID)

	// Confirmar a transação
	if err := tx.Commit(); err != nil {
		log.Fatalf("Failed to commit transaction: %v", err)
	}

	// Buscar o usuário pelo ID
	var user User
	err = supabase.QueryRow(`
		SELECT id, name, email, created_at, updated_at 
		FROM users 
		WHERE id = $1
	`, userID).Scan(&user.ID, &user.Name, &user.Email, &user.CreatedAt, &user.UpdatedAt)
	if err != nil {
		log.Fatalf("Failed to find user: %v", err)
	}

	fmt.Printf("Found user: %+v\n", user)

	// Atualizar o usuário
	_, err = supabase.Exec(`
		UPDATE users 
		SET name = $1, updated_at = $2
		WHERE id = $3
	`, "Jane Updated", time.Now(), userID)
	if err != nil {
		log.Fatalf("Failed to update user: %v", err)
	}

	fmt.Println("User updated")

	// Buscar todos os usuários
	rows, err := supabase.Query(`
		SELECT id, name, email, created_at, updated_at 
		FROM users
	`)
	if err != nil {
		log.Fatalf("Failed to query users: %v", err)
	}
	defer rows.Close()

	var users []User
	for rows.Next() {
		var u User
		if err := rows.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt, &u.UpdatedAt); err != nil {
			log.Fatalf("Failed to scan row: %v", err)
		}
		users = append(users, u)
	}

	if err := rows.Err(); err != nil {
		log.Fatalf("Error iterating rows: %v", err)
	}

	fmt.Printf("Found %d user(s)\n", len(users))
	for i, u := range users {
		fmt.Printf("%d. %s (%s)\n", i+1, u.Name, u.Email)
	}

	// Excluir o usuário
	_, err = supabase.Exec(`
		DELETE FROM users
		WHERE id = $1
	`, userID)
	if err != nil {
		log.Fatalf("Failed to delete user: %v", err)
	}

	fmt.Println("User deleted")
}

package test

import (
	"testing"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/validation"
)

// Estrutura de teste
type TestUser struct {
	Name     string `validate:"required,min=3,max=50"`
	Email    string `validate:"required,email"`
	Age      int    `validate:"required,min=18,max=120"`
	Password string `validate:"required,min=8"`
}

func TestValidateStruct(t *testing.T) {
	// Testes de validação com sucesso
	t.Run("Valid struct", func(t *testing.T) {
		user := TestUser{
			Name:     "John Doe",
			Email:    "john@example.com",
			Age:      30,
			Password: "password123",
		}

		errors, valid := validation.ValidateStruct(user)
		if !valid {
			t.Errorf("Expected validation to succeed, but it failed with errors: %v", errors)
		}
		if errors.HasErrors() {
			t.Errorf("Expected no validation errors, but got: %v", errors)
		}
	})

	// Testes de validação com falhas
	t.Run("Invalid email", func(t *testing.T) {
		user := TestUser{
			Name:     "John Doe",
			Email:    "invalid-email",
			Age:      30,
			Password: "password123",
		}

		errors, valid := validation.ValidateStruct(user)
		if valid {
			t.Error("Expected validation to fail, but it succeeded")
		}
		if !errors.HasErrors() {
			t.Error("Expected validation errors, but got none")
		}

		// Verificar se o erro está no campo correto
		hasEmailError := false
		for _, err := range errors {
			if err.Field == "Email" {
				hasEmailError = true
				break
			}
		}
		if !hasEmailError {
			t.Error("Expected error in Email field, but found none")
		}
	})

	t.Run("Multiple validation errors", func(t *testing.T) {
		user := TestUser{
			Name:     "Jo", // Muito curto
			Email:    "invalid-email",
			Age:      15, // Muito jovem
			Password: "123", // Muito curta
		}

		errors, valid := validation.ValidateStruct(user)
		if valid {
			t.Error("Expected validation to fail, but it succeeded")
		}
		if !errors.HasErrors() {
			t.Error("Expected validation errors, but got none")
		}

		// Verificar se temos erros em todos os campos
		expectedFields := map[string]bool{
			"Name":     false,
			"Email":    false,
			"Age":      false,
			"Password": false,
		}

		for _, err := range errors {
			expectedFields[err.Field] = true
		}

		for field, found := range expectedFields {
			if !found {
				t.Errorf("Expected error in %s field, but found none", field)
			}
		}
	})

	t.Run("Missing required fields", func(t *testing.T) {
		user := TestUser{
			// Todos os campos obrigatórios estão faltando
		}

		errors, valid := validation.ValidateStruct(user)
		if valid {
			t.Error("Expected validation to fail, but it succeeded")
		}
		if !errors.HasErrors() {
			t.Error("Expected validation errors, but got none")
		}

		// Verificar se temos erros em todos os campos
		expectedFields := map[string]bool{
			"Name":     false,
			"Email":    false,
			"Age":      false,
			"Password": false,
		}

		for _, err := range errors {
			expectedFields[err.Field] = true
		}

		for field, found := range expectedFields {
			if !found {
				t.Errorf("Expected error in %s field, but found none", field)
			}
		}
	})
}

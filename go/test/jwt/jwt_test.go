package test_jwt

import (
	"testing"
	"time"

	"github.com/systentandobr/toolkit/go/shared/security"
)

func TestJWTService(t *testing.T) {
	// Configuração do serviço JWT para teste
	config := security.JWTConfig{
		SecretKey:              "test-secret-key",
		AccessTokenExpiration:  5 * time.Minute,
		RefreshTokenExpiration: 24 * time.Hour,
		Issuer:                 "test-issuer",
	}
	service := security.NewJWTService(config)

	// Dados de teste
	userID := "user-123"
	username := "test-user"
	email := "test@example.com"
	roles := []string{"user", "admin"}
	metadata := map[string]interface{}{
		"foo": "bar",
	}

	t.Run("GenerateAccessToken", func(t *testing.T) {
		token, err := service.GenerateAccessToken(userID, username, email, roles, metadata)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}
		if token == "" {
			t.Error("Expected non-empty token")
		}
	})

	t.Run("GenerateRefreshToken", func(t *testing.T) {
		token, err := service.GenerateRefreshToken(userID)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}
		if token == "" {
			t.Error("Expected non-empty token")
		}
	})

	t.Run("GenerateTokens", func(t *testing.T) {
		tokens, err := service.GenerateTokens(userID, username, email, roles, metadata)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}
		if tokens.AccessToken == "" {
			t.Error("Expected non-empty access token")
		}
		if tokens.RefreshToken == "" {
			t.Error("Expected non-empty refresh token")
		}
		if tokens.ExpiresAt.Before(time.Now()) {
			t.Error("Expected expiration time in the future")
		}
		if tokens.TokenType != "Bearer" {
			t.Errorf("Expected token type 'Bearer', got '%s'", tokens.TokenType)
		}
	})

	t.Run("ValidateToken", func(t *testing.T) {
		// Gerar um token
		accessToken, err := service.GenerateAccessToken(userID, username, email, roles, metadata)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}

		// Validar o token
		claims, err := service.ValidateToken(accessToken)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}

		// Verificar os claims
		if claims.UserID != userID {
			t.Errorf("Expected UserID '%s', got '%s'", userID, claims.UserID)
		}
		if claims.Username != username {
			t.Errorf("Expected Username '%s', got '%s'", username, claims.Username)
		}
		if claims.Email != email {
			t.Errorf("Expected Email '%s', got '%s'", email, claims.Email)
		}
		if len(claims.Roles) != len(roles) {
			t.Errorf("Expected %d roles, got %d", len(roles), len(claims.Roles))
		}
		for i, role := range roles {
			if claims.Roles[i] != role {
				t.Errorf("Expected role '%s', got '%s'", role, claims.Roles[i])
			}
		}
		if claims.Metadata["foo"] != metadata["foo"] {
			t.Errorf("Expected metadata['foo'] = '%v', got '%v'", metadata["foo"], claims.Metadata["foo"])
		}
	})

	t.Run("InvalidToken", func(t *testing.T) {
		invalidToken := "invalid.token.format"
		_, err := service.ValidateToken(invalidToken)
		if err == nil {
			t.Error("Expected error for invalid token, got nil")
		}
	})

	t.Run("ExpiredToken", func(t *testing.T) {
		// Criar uma configuração com token de curta duração
		expiredConfig := security.JWTConfig{
			SecretKey:             "test-secret-key",
			AccessTokenExpiration: 1 * time.Nanosecond, // Expira imediatamente
			Issuer:                "test-issuer",
		}
		expiredService := security.NewJWTService(expiredConfig)

		// Gerar um token que expira imediatamente
		accessToken, err := expiredService.GenerateAccessToken(userID, username, email, roles, metadata)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}

		// Esperar para garantir que o token expirou
		time.Sleep(1 * time.Millisecond)

		// Validar o token expirado
		_, err = expiredService.ValidateToken(accessToken)
		if err != security.ErrJWTExpired {
			t.Errorf("Expected ErrJWTExpired, got %v", err)
		}
	})

	t.Run("RefreshAccessToken", func(t *testing.T) {
		// Gerar tokens
		tokens, err := service.GenerateTokens(userID, username, email, roles, metadata)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}

		// Atualizar o token de acesso
		newTokens, err := service.RefreshAccessToken(tokens.RefreshToken)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}

		// Verificar os novos tokens
		if newTokens.AccessToken == "" {
			t.Error("Expected non-empty access token")
		}
		if newTokens.RefreshToken == "" {
			t.Error("Expected non-empty refresh token")
		}
		if newTokens.AccessToken == tokens.AccessToken {
			t.Error("Expected new access token to be different from the original")
		}
		if newTokens.ExpiresAt.Before(time.Now()) {
			t.Error("Expected expiration time in the future")
		}
	})
}

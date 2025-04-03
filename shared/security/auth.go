package security

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"errors"
	"fmt"
	"strings"
	"time"

	"golang.org/x/crypto/bcrypt"
)

var (
	ErrInvalidToken       = errors.New("token inválido")
	ErrTokenExpired       = errors.New("token expirado")
	ErrPasswordMismatch   = errors.New("senha incorreta")
	ErrPasswordTooWeak    = errors.New("senha muito fraca")
	ErrPasswordGeneration = errors.New("erro ao gerar hash de senha")
)

// HashPassword gera um hash da senha usando bcrypt
func HashPassword(password string) (string, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", fmt.Errorf("%w: %v", ErrPasswordGeneration, err)
	}
	return string(hash), nil
}

// ComparePasswords compara uma senha com seu hash
func ComparePasswords(hashedPassword, plainPassword string) error {
	err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(plainPassword))
	if err != nil {
		return ErrPasswordMismatch
	}
	return nil
}

// GenerateSecureToken gera um token seguro com o tamanho informado
func GenerateSecureToken(length int) (string, error) {
	b := make([]byte, length)
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(b), nil
}

// IsStrongPassword verifica se uma senha é forte
func IsStrongPassword(password string) bool {
	if len(password) < 8 {
		return false
	}
	
	hasUpper := false
	hasLower := false
	hasNumber := false
	hasSpecial := false
	
	for _, char := range password {
		switch {
		case 'a' <= char && char <= 'z':
			hasLower = true
		case 'A' <= char && char <= 'Z':
			hasUpper = true
		case '0' <= char && char <= '9':
			hasNumber = true
		case strings.ContainsRune("!@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`", char):
			hasSpecial = true
		}
	}
	
	return hasUpper && hasLower && hasNumber && hasSpecial
}

// ConstantTimeEquals compara duas strings em tempo constante
func ConstantTimeEquals(a, b string) bool {
	return subtle.ConstantTimeCompare([]byte(a), []byte(b)) == 1
}

// Token representa a estrutura básica de um token
type Token struct {
	AccessToken  string    `json:"access_token"`
	RefreshToken string    `json:"refresh_token,omitempty"`
	ExpiresAt    time.Time `json:"expires_at"`
	TokenType    string    `json:"token_type"`
}

// IsExpired verifica se o token está expirado
func (t *Token) IsExpired() bool {
	return time.Now().After(t.ExpiresAt)
}

// RemainingTime retorna o tempo restante de validade do token
func (t *Token) RemainingTime() time.Duration {
	if t.IsExpired() {
		return 0
	}
	return t.ExpiresAt.Sub(time.Now())
}

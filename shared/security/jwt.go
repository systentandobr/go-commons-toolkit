package security

import (
	"errors"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var (
	ErrJWTInvalid       = errors.New("token JWT inválido")
	ErrJWTExpired       = errors.New("token JWT expirado")
	ErrJWTSigningMethod = errors.New("método de assinatura inválido")
	ErrJWTClaims        = errors.New("claims inválidas")
)

// JWTConfig representa as configurações para o JWT
type JWTConfig struct {
	// Chave secreta para assinatura dos tokens
	SecretKey string
	// Tempo de expiração do token de acesso
	AccessTokenExpiration time.Duration
	// Tempo de expiração do token de atualização
	RefreshTokenExpiration time.Duration
	// Emissor do token
	Issuer string
}

// DefaultJWTConfig retorna configurações padrão para JWT
func DefaultJWTConfig() JWTConfig {
	return JWTConfig{
		SecretKey:             "your-secret-key-change-me-in-production",
		AccessTokenExpiration: 15 * time.Minute,
		RefreshTokenExpiration: 24 * time.Hour * 7, // 7 dias
		Issuer:                "go-commons-toolkit",
	}
}

// CustomClaims representa as claims personalizadas do JWT
type CustomClaims struct {
	UserID   string                 `json:"user_id,omitempty"`
	Username string                 `json:"username,omitempty"`
	Email    string                 `json:"email,omitempty"`
	Roles    []string               `json:"roles,omitempty"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
	jwt.RegisteredClaims
}

// JWTService representa o serviço de gerenciamento de JWT
type JWTService struct {
	config JWTConfig
}

// NewJWTService cria um novo serviço de JWT
func NewJWTService(config JWTConfig) *JWTService {
	return &JWTService{
		config: config,
	}
}

// GenerateAccessToken gera um novo token de acesso JWT
func (s *JWTService) GenerateAccessToken(userID, username, email string, roles []string, metadata map[string]interface{}) (string, error) {
	now := time.Now()
	expiresAt := now.Add(s.config.AccessTokenExpiration)

	claims := CustomClaims{
		UserID:   userID,
		Username: username,
		Email:    email,
		Roles:    roles,
		Metadata: metadata,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    s.config.Issuer,
			Subject:   userID,
			IssuedAt:  jwt.NewNumericDate(now),
			ExpiresAt: jwt.NewNumericDate(expiresAt),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signedToken, err := token.SignedString([]byte(s.config.SecretKey))
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	return signedToken, nil
}

// GenerateRefreshToken gera um novo token de atualização JWT
func (s *JWTService) GenerateRefreshToken(userID string) (string, error) {
	now := time.Now()
	expiresAt := now.Add(s.config.RefreshTokenExpiration)

	claims := jwt.RegisteredClaims{
		Issuer:    s.config.Issuer,
		Subject:   userID,
		IssuedAt:  jwt.NewNumericDate(now),
		ExpiresAt: jwt.NewNumericDate(expiresAt),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	signedToken, err := token.SignedString([]byte(s.config.SecretKey))
	if err != nil {
		return "", fmt.Errorf("failed to sign refresh token: %w", err)
	}

	return signedToken, nil
}

// GenerateTokens gera um par de tokens (acesso e atualização)
func (s *JWTService) GenerateTokens(userID, username, email string, roles []string, metadata map[string]interface{}) (*Token, error) {
	accessToken, err := s.GenerateAccessToken(userID, username, email, roles, metadata)
	if err != nil {
		return nil, err
	}

	refreshToken, err := s.GenerateRefreshToken(userID)
	if err != nil {
		return nil, err
	}

	expiresAt := time.Now().Add(s.config.AccessTokenExpiration)

	return &Token{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		ExpiresAt:    expiresAt,
		TokenType:    "Bearer",
	}, nil
}

// ValidateToken valida um token JWT
func (s *JWTService) ValidateToken(tokenString string) (*CustomClaims, error) {
	// Parse do token
	token, err := jwt.ParseWithClaims(tokenString, &CustomClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Validar o método de assinatura
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, ErrJWTSigningMethod
		}
		return []byte(s.config.SecretKey), nil
	})

	if err != nil {
		if errors.Is(err, jwt.ErrTokenExpired) {
			return nil, ErrJWTExpired
		}
		return nil, fmt.Errorf("%w: %v", ErrJWTInvalid, err)
	}

	// Verificar se o token é válido
	if !token.Valid {
		return nil, ErrJWTInvalid
	}

	// Extrair claims
	claims, ok := token.Claims.(*CustomClaims)
	if !ok {
		return nil, ErrJWTClaims
	}

	return claims, nil
}

// RefreshAccessToken gera um novo token de acesso a partir de um token de atualização
func (s *JWTService) RefreshAccessToken(refreshToken string) (*Token, error) {
	// Validar token de atualização
	token, err := jwt.ParseWithClaims(refreshToken, &jwt.RegisteredClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, ErrJWTSigningMethod
		}
		return []byte(s.config.SecretKey), nil
	})

	if err != nil {
		if errors.Is(err, jwt.ErrTokenExpired) {
			return nil, ErrJWTExpired
		}
		return nil, fmt.Errorf("%w: %v", ErrJWTInvalid, err)
	}

	// Verificar se o token é válido
	if !token.Valid {
		return nil, ErrJWTInvalid
	}

	// Extrair claims
	claims, ok := token.Claims.(*jwt.RegisteredClaims)
	if !ok {
		return nil, ErrJWTClaims
	}

	// Gerar novo token de acesso
	userID := claims.Subject
	
	// Aqui normalmente buscaríamos o usuário no banco de dados para obter mais informações
	// Como exemplo, vamos gerar um token simplificado
	accessToken, err := s.GenerateAccessToken(userID, "", "", nil, nil)
	if err != nil {
		return nil, err
	}

	// Gerar novo token de atualização
	newRefreshToken, err := s.GenerateRefreshToken(userID)
	if err != nil {
		return nil, err
	}

	expiresAt := time.Now().Add(s.config.AccessTokenExpiration)

	return &Token{
		AccessToken:  accessToken,
		RefreshToken: newRefreshToken,
		ExpiresAt:    expiresAt,
		TokenType:    "Bearer",
	}, nil
}

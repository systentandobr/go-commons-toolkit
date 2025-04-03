package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/config"
	http_toolkit "github.com/systentandobr/go-commons-toolkit/shared/infrastructure/http"
	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/validation"
	"github.com/systentandobr/go-commons-toolkit/shared/security"
)

// UserRegisterRequest representa uma requisição de registro de usuário
type UserRegisterRequest struct {
	Name     string `json:"name" validate:"required,min=3,max=100"`
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required,min=8"`
	Age      int    `json:"age" validate:"required,min=18"`
}

// UserLoginRequest representa uma requisição de login
type UserLoginRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required"`
}

// Handlers
func handleRegister(w http.ResponseWriter, r *http.Request) {
	// Verificar se o método é POST
	if r.Method != http.MethodPost {
		http_toolkit.RespondWithMethodNotAllowed(w, "Apenas POST é permitido")
		return
	}

	// Decodificar o corpo da requisição
	var req UserRegisterRequest
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&req); err != nil {
		http_toolkit.RespondWithBadRequest(w, "Corpo da requisição inválido")
		return
	}

	// Validar a requisição
	if errors, valid := validation.ValidateStruct(req); !valid {
		http_toolkit.RespondWithValidationError(w, "Erro de validação", errors)
		return
	}

	// Processar o registro (simulado)
	// Em um caso real, salvaríamos no banco de dados
	hashedPassword, err := security.HashPassword(req.Password)
	if err != nil {
		http_toolkit.RespondWithInternalError(w, "Erro ao processar a senha")
		return
	}

	// Simular o usuário criado
	response := map[string]interface{}{
		"id":    "user-123",
		"name":  req.Name,
		"email": req.Email,
		// Nunca retornar a senha, mesmo que em hash
	}

	fmt.Printf("Usuário registrado: %s (%s) com senha hash: %s\n", req.Name, req.Email, hashedPassword)

	// Responder com sucesso
	http_toolkit.RespondWithCreated(w, response)
}

func handleLogin(w http.ResponseWriter, r *http.Request) {
	// Verificar se o método é POST
	if r.Method != http.MethodPost {
		http_toolkit.RespondWithMethodNotAllowed(w, "Apenas POST é permitido")
		return
	}

	// Decodificar o corpo da requisição
	var req UserLoginRequest
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&req); err != nil {
		http_toolkit.RespondWithBadRequest(w, "Corpo da requisição inválido")
		return
	}

	// Validar a requisição
	if errors, valid := validation.ValidateStruct(req); !valid {
		http_toolkit.RespondWithValidationError(w, "Erro de validação", errors)
		return
	}

	// Validar credenciais (simulado)
	// Em um caso real, verificaríamos no banco de dados
	if req.Email != "user@example.com" || req.Password != "password123" {
		http_toolkit.RespondWithUnauthorized(w, "Credenciais inválidas")
		return
	}

	// Configurar serviço JWT
	jwtConfig := security.DefaultJWTConfig()
	jwtService := security.NewJWTService(jwtConfig)

	// Gerar tokens
	token, err := jwtService.GenerateTokens("user-123", "User Example", req.Email, []string{"user"}, nil)
	if err != nil {
		http_toolkit.RespondWithInternalError(w, "Erro ao gerar tokens")
		return
	}

	// Responder com sucesso
	http_toolkit.RespondWithSuccess(w, token)
}

func handleSecure(w http.ResponseWriter, r *http.Request) {
	// Este endpoint está protegido por middleware JWT
	// As claims do usuário já estão disponíveis no contexto
	
	claims, ok := http_toolkit.GetUserClaims(r.Context())
	if !ok {
		http_toolkit.RespondWithUnauthorized(w, "Não autorizado")
		return
	}

	// Responder com dados do usuário
	response := map[string]interface{}{
		"message": "Você está autenticado!",
		"user_id": claims.UserID,
		"username": claims.Username,
		"email": claims.Email,
		"roles": claims.Roles,
	}

	http_toolkit.RespondWithSuccess(w, response)
}

func main() {
	// Carregar configurações
	if err := config.LoadEnv("../../.env"); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	// Configurar serviço JWT
	jwtConfig := security.DefaultJWTConfig()
	jwtService := security.NewJWTService(jwtConfig)

	// Configurar middlewares
	corsMiddleware := http_toolkit.CORSMiddleware([]string{"*"})
	loggingMiddleware := http_toolkit.LoggingMiddleware()
	recoveryMiddleware := http_toolkit.RecoveryMiddleware()
	jwtMiddleware := http_toolkit.JWTAuthMiddleware(jwtService)
	adminMiddleware := http_toolkit.RoleCheckMiddleware("admin")

	// Criar um manipulador para o endpoint público de registro
	http.Handle("/api/register", corsMiddleware(loggingMiddleware(recoveryMiddleware(http.HandlerFunc(handleRegister)))))

	// Criar um manipulador para o endpoint público de login
	http.Handle("/api/login", corsMiddleware(loggingMiddleware(recoveryMiddleware(http.HandlerFunc(handleLogin)))))

	// Criar um manipulador para o endpoint seguro que requer autenticação
	http.Handle("/api/secure", corsMiddleware(loggingMiddleware(recoveryMiddleware(jwtMiddleware(http.HandlerFunc(handleSecure))))))

	// Criar um manipulador para o endpoint seguro que requer role de admin
	http.Handle("/api/admin", corsMiddleware(loggingMiddleware(recoveryMiddleware(jwtMiddleware(adminMiddleware(http.HandlerFunc(handleSecure)))))))

	// Iniciar o servidor
	fmt.Println("Servidor HTTP iniciado na porta 8080")
	cfg := config.Get()
	if err := http.ListenAndServe(fmt.Sprintf(":%d", cfg.HTTPPort), nil); err != nil {
		log.Fatalf("Erro ao iniciar o servidor: %v", err)
	}
}

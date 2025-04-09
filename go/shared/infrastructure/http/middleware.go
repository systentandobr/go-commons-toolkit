package http

import (
	"context"
	"net/http"
	"strings"

	"github.com/systentandobr/toolkit/go/shared/security"
)

// Middleware representa um middleware HTTP
type Middleware func(http.Handler) http.Handler

// Chain encadeia múltiplos middlewares
func Chain(middlewares ...Middleware) Middleware {
	return func(next http.Handler) http.Handler {
		for i := len(middlewares) - 1; i >= 0; i-- {
			next = middlewares[i](next)
		}
		return next
	}
}

// contextKey é um tipo para chaves de contexto
type contextKey string

// Constantes para chaves de contexto
const (
	UserClaimsKey contextKey = "userClaims"
	UserIDKey     contextKey = "userID"
	RolesKey      contextKey = "roles"
)

// JWTAuthMiddleware retorna um middleware que valida tokens JWT
func JWTAuthMiddleware(jwtService *security.JWTService) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extrair token do cabeçalho Authorization
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				RespondWithUnauthorized(w, "Authorization header required")
				return
			}

			// O token é enviado como "Bearer <token>"
			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" {
				RespondWithUnauthorized(w, "Invalid authorization format")
				return
			}

			tokenString := parts[1]

			// Validar o token
			claims, err := jwtService.ValidateToken(tokenString)
			if err != nil {
				switch err {
				case security.ErrJWTExpired:
					RespondWithUnauthorized(w, "Token expired")
				default:
					RespondWithUnauthorized(w, "Invalid token")
				}
				return
			}

			// Adicionar claims ao contexto
			ctx := context.WithValue(r.Context(), UserClaimsKey, claims)
			ctx = context.WithValue(ctx, UserIDKey, claims.UserID)
			ctx = context.WithValue(ctx, RolesKey, claims.Roles)

			// Chamar o próximo handler com o contexto atualizado
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// RoleCheckMiddleware retorna um middleware que verifica se o usuário tem as roles necessárias
func RoleCheckMiddleware(requiredRoles ...string) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Extrair roles do contexto
			rolesValue := r.Context().Value(RolesKey)
			if rolesValue == nil {
				RespondWithUnauthorized(w, "No role information found")
				return
			}

			userRoles, ok := rolesValue.([]string)
			if !ok {
				RespondWithInternalError(w, "Invalid role information")
				return
			}

			// Verificar se o usuário tem pelo menos uma das roles necessárias
			hasRequiredRole := false
			for _, requiredRole := range requiredRoles {
				for _, userRole := range userRoles {
					if requiredRole == userRole {
						hasRequiredRole = true
						break
					}
				}
				if hasRequiredRole {
					break
				}
			}

			if !hasRequiredRole {
				RespondWithForbidden(w, "Insufficient permissions")
				return
			}

			// Chamar o próximo handler
			next.ServeHTTP(w, r)
		})
	}
}

// CORSMiddleware retorna um middleware para lidar com CORS
func CORSMiddleware(allowedOrigins []string) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Verificar a origem
			origin := r.Header.Get("Origin")

			allowOrigin := ""
			if len(allowedOrigins) == 0 || contains(allowedOrigins, "*") {
				// Se não houver origens especificadas ou "*" for permitido, aceitar qualquer origem
				allowOrigin = "*"
			} else if contains(allowedOrigins, origin) {
				// Se a origem estiver na lista, permitir
				allowOrigin = origin
			}

			// Se uma origem foi permitida, adicionar os cabeçalhos CORS
			if allowOrigin != "" {
				w.Header().Set("Access-Control-Allow-Origin", allowOrigin)
				w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
				w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
				w.Header().Set("Access-Control-Max-Age", "86400") // 24 horas

				// Lidar com requisições OPTIONS (preflight)
				if r.Method == "OPTIONS" {
					w.WriteHeader(http.StatusOK)
					return
				}
			}

			// Chamar o próximo handler
			next.ServeHTTP(w, r)
		})
	}
}

// LoggingMiddleware retorna um middleware que registra informações da requisição
func LoggingMiddleware() Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Registrar informações da requisição antes de processá-la
			// Em uma implementação real, usaríamos um logger estruturado

			// Chamar o próximo handler
			next.ServeHTTP(w, r)

			// Registrar informações após o processamento
		})
	}
}

// RecoveryMiddleware retorna um middleware que recupera de pânicos
func RecoveryMiddleware() Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if err := recover(); err != nil {
					// Registrar o erro
					// Em uma implementação real, usaríamos um logger estruturado

					// Responder com erro interno
					RespondWithInternalError(w, "Internal server error")
				}
			}()

			// Chamar o próximo handler
			next.ServeHTTP(w, r)
		})
	}
}

// contains verifica se um slice contém um valor
func contains(slice []string, value string) bool {
	for _, item := range slice {
		if item == value {
			return true
		}
	}
	return false
}

// GetUserID retorna o ID do usuário do contexto
func GetUserID(ctx context.Context) (string, bool) {
	id, ok := ctx.Value(UserIDKey).(string)
	return id, ok
}

// GetUserClaims retorna as claims do usuário do contexto
func GetUserClaims(ctx context.Context) (*security.CustomClaims, bool) {
	claims, ok := ctx.Value(UserClaimsKey).(*security.CustomClaims)
	return claims, ok
}

// GetUserRoles retorna as roles do usuário do contexto
func GetUserRoles(ctx context.Context) ([]string, bool) {
	roles, ok := ctx.Value(RolesKey).([]string)
	return roles, ok
}

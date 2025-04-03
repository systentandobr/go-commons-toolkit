package http

import (
	"encoding/json"
	"net/http"

	"github.com/systentandobr/go-commons-toolkit/shared/infrastructure/validation"
)

// Response representa uma resposta HTTP padronizada
type Response struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   *ErrorInfo  `json:"error,omitempty"`
}

// ErrorInfo representa informações de erro
type ErrorInfo struct {
	Code    string                      `json:"code"`
	Message string                      `json:"message"`
	Details validation.ValidationErrors `json:"details,omitempty"`
}

// NewSuccessResponse cria uma nova resposta de sucesso
func NewSuccessResponse(data interface{}) Response {
	return Response{
		Success: true,
		Data:    data,
	}
}

// NewErrorResponse cria uma nova resposta de erro
func NewErrorResponse(code string, message string) Response {
	return Response{
		Success: false,
		Error: &ErrorInfo{
			Code:    code,
			Message: message,
		},
	}
}

// NewValidationErrorResponse cria uma nova resposta de erro de validação
func NewValidationErrorResponse(message string, errors validation.ValidationErrors) Response {
	return Response{
		Success: false,
		Error: &ErrorInfo{
			Code:    "VALIDATION_ERROR",
			Message: message,
			Details: errors,
		},
	}
}

// WriteJSON escreve uma resposta JSON
func WriteJSON(w http.ResponseWriter, statusCode int, response interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}

// RespondWithSuccess envia uma resposta de sucesso
func RespondWithSuccess(w http.ResponseWriter, data interface{}) {
	WriteJSON(w, http.StatusOK, NewSuccessResponse(data))
}

// RespondWithCreated envia uma resposta de criação bem-sucedida
func RespondWithCreated(w http.ResponseWriter, data interface{}) {
	WriteJSON(w, http.StatusCreated, NewSuccessResponse(data))
}

// RespondWithError envia uma resposta de erro
func RespondWithError(w http.ResponseWriter, statusCode int, code string, message string) {
	WriteJSON(w, statusCode, NewErrorResponse(code, message))
}

// RespondWithValidationError envia uma resposta de erro de validação
func RespondWithValidationError(w http.ResponseWriter, message string, errors validation.ValidationErrors) {
	WriteJSON(w, http.StatusBadRequest, NewValidationErrorResponse(message, errors))
}

// RespondWithBadRequest envia uma resposta de requisição inválida
func RespondWithBadRequest(w http.ResponseWriter, message string) {
	RespondWithError(w, http.StatusBadRequest, "BAD_REQUEST", message)
}

// RespondWithUnauthorized envia uma resposta de não autorizado
func RespondWithUnauthorized(w http.ResponseWriter, message string) {
	RespondWithError(w, http.StatusUnauthorized, "UNAUTHORIZED", message)
}

// RespondWithForbidden envia uma resposta de acesso proibido
func RespondWithForbidden(w http.ResponseWriter, message string) {
	RespondWithError(w, http.StatusForbidden, "FORBIDDEN", message)
}

// RespondWithNotFound envia uma resposta de recurso não encontrado
func RespondWithNotFound(w http.ResponseWriter, message string) {
	RespondWithError(w, http.StatusNotFound, "NOT_FOUND", message)
}

// RespondWithInternalError envia uma resposta de erro interno
func RespondWithInternalError(w http.ResponseWriter, message string) {
	RespondWithError(w, http.StatusInternalServerError, "INTERNAL_ERROR", message)
}

// RespondWithMethodNotAllowed envia uma resposta de método não permitido
func RespondWithMethodNotAllowed(w http.ResponseWriter, message string) {
	RespondWithError(w, http.StatusMethodNotAllowed, "METHOD_NOT_ALLOWED", message)
}

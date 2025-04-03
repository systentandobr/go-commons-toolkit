package utils

import (
	"fmt"
	"runtime"
)

// AppError representa um erro da aplicação
type AppError struct {
	Code      string
	Message   string
	Details   interface{}
	Cause     error
	StackInfo string
}

// NewAppError cria um novo erro da aplicação
func NewAppError(code, message string, details interface{}, cause error) *AppError {
	_, file, line, ok := runtime.Caller(1)
	stackInfo := "unknown"
	if ok {
		stackInfo = fmt.Sprintf("%s:%d", file, line)
	}

	return &AppError{
		Code:      code,
		Message:   message,
		Details:   details,
		Cause:     cause,
		StackInfo: stackInfo,
	}
}

// Error implementa a interface error
func (e *AppError) Error() string {
	if e.Cause != nil {
		return fmt.Sprintf("[%s] %s: %v (at %s)", e.Code, e.Message, e.Cause, e.StackInfo)
	}
	return fmt.Sprintf("[%s] %s (at %s)", e.Code, e.Message, e.StackInfo)
}

// Unwrap implementa a interface para unwrap de erros
func (e *AppError) Unwrap() error {
	return e.Cause
}

// Common error codes
const (
	ErrCodeValidation   = "VALIDATION_ERROR"
	ErrCodeNotFound     = "NOT_FOUND"
	ErrCodeUnauthorized = "UNAUTHORIZED"
	ErrCodeForbidden    = "FORBIDDEN"
	ErrCodeInternal     = "INTERNAL_ERROR"
	ErrCodeDatabase     = "DATABASE_ERROR"
	ErrCodeExternal     = "EXTERNAL_SERVICE_ERROR"
)

// Wrapper functions for common error types

// ValidationError cria um novo erro de validação
func ValidationError(message string, details interface{}, cause error) *AppError {
	return NewAppError(ErrCodeValidation, message, details, cause)
}

// NotFoundError cria um novo erro de recurso não encontrado
func NotFoundError(message string, cause error) *AppError {
	return NewAppError(ErrCodeNotFound, message, nil, cause)
}

// UnauthorizedError cria um novo erro de não autorizado
func UnauthorizedError(message string, cause error) *AppError {
	return NewAppError(ErrCodeUnauthorized, message, nil, cause)
}

// ForbiddenError cria um novo erro de acesso proibido
func ForbiddenError(message string, cause error) *AppError {
	return NewAppError(ErrCodeForbidden, message, nil, cause)
}

// InternalError cria um novo erro interno
func InternalError(message string, cause error) *AppError {
	return NewAppError(ErrCodeInternal, message, nil, cause)
}

// DatabaseError cria um novo erro de banco de dados
func DatabaseError(message string, cause error) *AppError {
	return NewAppError(ErrCodeDatabase, message, nil, cause)
}

// ExternalServiceError cria um novo erro de serviço externo
func ExternalServiceError(message string, cause error) *AppError {
	return NewAppError(ErrCodeExternal, message, nil, cause)
}

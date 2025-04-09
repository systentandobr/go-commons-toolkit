// pkg/common/errors/errors.go
package utils

import (
	"errors"
	"fmt"
)

// ErrorType representa os diferentes tipos de erros
type ErrorType string

const (
	// Tipos de erro
	TypeValidation   ErrorType = "VALIDATION"   // Erro de validação
	TypeNotFound     ErrorType = "NOT_FOUND"    // Recurso não encontrado
	TypeDuplicated   ErrorType = "DUPLICATED"   // Recurso duplicado
	TypeUnauthorized ErrorType = "UNAUTHORIZED" // Acesso não autorizado
	TypeForbidden    ErrorType = "FORBIDDEN"    // Acesso proibido
	TypeInternal     ErrorType = "INTERNAL"     // Erro interno do servidor
	TypeExternal     ErrorType = "EXTERNAL"     // Erro de serviço externo
	TypeTimeout      ErrorType = "TIMEOUT"      // Erro de timeout
	TypeBadGateway   ErrorType = "BAD_GATEWAY"  // Erro de gateway
	TypeUnavailable  ErrorType = "UNAVAILABLE"  // Serviço indisponível
)

// AppError representa um erro da aplicação
type AppError struct {
	Type       ErrorType
	Message    string
	Details    map[string]interface{}
	StatusCode int
	OrigErr    error
}

// Error implementa a interface error
func (e *AppError) Error() string {
	if e.OrigErr != nil {
		return fmt.Sprintf("%s: %s [%s]", e.Type, e.Message, e.OrigErr.Error())
	}
	return fmt.Sprintf("%s: %s", e.Type, e.Message)
}

// Unwrap implementa a interface de unwrapping
func (e *AppError) Unwrap() error {
	return e.OrigErr
}

// Is implementa a interface de comparação
func (e *AppError) Is(target error) bool {
	t, ok := target.(*AppError)
	if !ok {
		return false
	}
	return e.Type == t.Type
}

// WithDetails adiciona detalhes ao erro
func (e *AppError) WithDetails(details map[string]interface{}) *AppError {
	if e.Details == nil {
		e.Details = make(map[string]interface{})
	}
	for k, v := range details {
		e.Details[k] = v
	}
	return e
}

// Funções para criar erros específicos

// NewValidationError cria um erro de validação
func NewValidationError(message string, details map[string]interface{}, origErr error) *AppError {
	return &AppError{
		Type:       TypeValidation,
		Message:    message,
		Details:    details,
		StatusCode: 400,
		OrigErr:    origErr,
	}
}

// NewNotFoundError cria um erro de recurso não encontrado
func NewNotFoundError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeNotFound,
		Message:    message,
		StatusCode: 404,
		OrigErr:    origErr,
	}
}

// NewDuplicatedError cria um erro de recurso duplicado
func NewDuplicatedError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeDuplicated,
		Message:    message,
		StatusCode: 409,
		OrigErr:    origErr,
	}
}

// NewUnauthorizedError cria um erro de acesso não autorizado
func NewUnauthorizedError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeUnauthorized,
		Message:    message,
		StatusCode: 401,
		OrigErr:    origErr,
	}
}

// NewForbiddenError cria um erro de acesso proibido
func NewForbiddenError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeForbidden,
		Message:    message,
		StatusCode: 403,
		OrigErr:    origErr,
	}
}

// NewInternalError cria um erro interno do servidor
func NewInternalError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeInternal,
		Message:    message,
		StatusCode: 500,
		OrigErr:    origErr,
	}
}

// NewExternalError cria um erro de serviço externo
func NewExternalError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeExternal,
		Message:    message,
		StatusCode: 502,
		OrigErr:    origErr,
	}
}

// NewTimeoutError cria um erro de timeout
func NewTimeoutError(message string, origErr error) *AppError {
	return &AppError{
		Type:       TypeTimeout,
		Message:    message,
		StatusCode: 504,
		OrigErr:    origErr,
	}
}

// IsValidationError verifica se o erro é do tipo validação
func IsValidationError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeValidation
	}
	return false
}

// IsNotFoundError verifica se o erro é do tipo não encontrado
func IsNotFoundError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeNotFound
	}
	return false
}

// IsDuplicatedError verifica se o erro é do tipo duplicado
func IsDuplicatedError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeDuplicated
	}
	return false
}

// IsUnauthorizedError verifica se o erro é do tipo não autorizado
func IsUnauthorizedError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeUnauthorized
	}
	return false
}

// IsForbiddenError verifica se o erro é do tipo proibido
func IsForbiddenError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeForbidden
	}
	return false
}

// IsInternalError verifica se o erro é do tipo interno
func IsInternalError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeInternal
	}
	return false
}

// IsExternalError verifica se o erro é do tipo externo
func IsExternalError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeExternal
	}
	return false
}

// IsTimeoutError verifica se o erro é do tipo timeout
func IsTimeoutError(err error) bool {
	var appErr *AppError
	if errors.As(err, &appErr) {
		return appErr.Type == TypeTimeout
	}
	return false
}

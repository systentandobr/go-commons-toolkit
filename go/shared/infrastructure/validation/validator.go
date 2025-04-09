package validation

import (
	"fmt"
	"strings"

	"github.com/go-playground/validator/v10"
)

var validate *validator.Validate

func init() {
	validate = validator.New()
}

// ValidationError representa um erro de validação
type ValidationError struct {
	Field   string `json:"field"`
	Message string `json:"message"`
}

// ValidationErrors representa uma coleção de erros de validação
type ValidationErrors []ValidationError

// Error implementa a interface error
func (ve ValidationErrors) Error() string {
	errorMessages := make([]string, 0, len(ve))
	for _, err := range ve {
		errorMessages = append(errorMessages, fmt.Sprintf("%s: %s", err.Field, err.Message))
	}
	return strings.Join(errorMessages, "; ")
}

// HasErrors retorna true se houver erros de validação
func (ve ValidationErrors) HasErrors() bool {
	return len(ve) > 0
}

// ValidateStruct valida uma estrutura com base nas tags de validação
func ValidateStruct(s interface{}) (ValidationErrors, bool) {
	var validationErrors ValidationErrors

	err := validate.Struct(s)
	if err == nil {
		return validationErrors, true
	}

	// Converte os erros de validação para o nosso formato
	for _, err := range err.(validator.ValidationErrors) {
		field := getFieldName(err.Field())
		message := getErrorMessage(err)
		validationErrors = append(validationErrors, ValidationError{
			Field:   field,
			Message: message,
		})
	}

	return validationErrors, false
}

// getFieldName retorna o nome do campo, podendo ser customizado
func getFieldName(field string) string {
	return field
}

// getErrorMessage retorna uma mensagem de erro legível para cada tipo de erro de validação
func getErrorMessage(err validator.FieldError) string {
	switch err.Tag() {
	case "required":
		return "Este campo é obrigatório"
	case "email":
		return "Deve ser um email válido"
	case "min":
		return fmt.Sprintf("Deve ter no mínimo %s caracteres", err.Param())
	case "max":
		return fmt.Sprintf("Deve ter no máximo %s caracteres", err.Param())
	case "oneof":
		return fmt.Sprintf("Deve ser um dos seguintes valores: %s", err.Param())
	default:
		return fmt.Sprintf("Erro de validação: %s", err.Tag())
	}
}

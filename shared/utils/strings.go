package utils

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"unicode"
)

// IsEmpty verifica se uma string está vazia
func IsEmpty(s string) bool {
	return strings.TrimSpace(s) == ""
}

// IsNotEmpty verifica se uma string não está vazia
func IsNotEmpty(s string) bool {
	return !IsEmpty(s)
}

// Truncate limita o tamanho de uma string
func Truncate(s string, maxLength int) string {
	if len(s) <= maxLength {
		return s
	}
	return s[:maxLength]
}

// TruncateWithEllipsis limita o tamanho de uma string e adiciona reticências
func TruncateWithEllipsis(s string, maxLength int) string {
	if len(s) <= maxLength {
		return s
	}
	return s[:maxLength-3] + "..."
}

// RemoveWhitespace remove todos os espaços em branco de uma string
func RemoveWhitespace(s string) string {
	return strings.Map(func(r rune) rune {
		if unicode.IsSpace(r) {
			return -1
		}
		return r
	}, s)
}

// RemoveSpecialChars remove caracteres especiais de uma string
func RemoveSpecialChars(s string) string {
	reg := regexp.MustCompile(`[^a-zA-Z0-9 ]+`)
	return reg.ReplaceAllString(s, "")
}

// Slugify converte uma string em um slug (URL amigável)
func Slugify(s string) string {
	// Converte para minúsculas
	s = strings.ToLower(s)

	// Remove caracteres especiais
	s = RemoveSpecialChars(s)

	// Substitui espaços por hífens
	s = regexp.MustCompile(`\s+`).ReplaceAllString(s, "-")

	// Remove hífens consecutivos
	s = regexp.MustCompile(`-+`).ReplaceAllString(s, "-")

	// Remove hífens no início e no fim
	s = strings.Trim(s, "-")

	return s
}

// GenerateRandomString gera uma string aleatória com o tamanho informado
func GenerateRandomString(length int) (string, error) {
	b := make([]byte, length)
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}

	return base64.URLEncoding.EncodeToString(b)[:length], nil
}

// MaskEmail mascara parte de um e-mail
func MaskEmail(email string) string {
	if IsEmpty(email) {
		return ""
	}

	parts := strings.Split(email, "@")
	if len(parts) != 2 {
		return email
	}

	username := parts[0]
	domain := parts[1]

	if len(username) <= 2 {
		return email
	}

	maskedUsername := username[:2] + strings.Repeat("*", len(username)-2)
	return maskedUsername + "@" + domain
}

// MaskPhone mascara parte de um número de telefone
func MaskPhone(phone string) string {
	if IsEmpty(phone) {
		return ""
	}

	// Remove caracteres não numéricos
	phone = regexp.MustCompile(`\D`).ReplaceAllString(phone, "")

	if len(phone) <= 4 {
		return phone
	}

	visibleDigits := 4
	maskedDigits := len(phone) - visibleDigits

	return strings.Repeat("*", maskedDigits) + phone[maskedDigits:]
}

// ContainsAny verifica se uma string contém qualquer uma das substrings informadas
func ContainsAny(s string, substrings ...string) bool {
	for _, sub := range substrings {
		if strings.Contains(s, sub) {
			return true
		}
	}
	return false
}

// ToSnakeCase converte uma string em snake_case
func ToSnakeCase(s string) string {
	var result strings.Builder

	for i, r := range s {
		if unicode.IsUpper(r) {
			if i > 0 {
				result.WriteRune('_')
			}
			result.WriteRune(unicode.ToLower(r))
		} else {
			result.WriteRune(r)
		}
	}

	return result.String()
}

// ToCamelCase converte uma string em camelCase
func ToCamelCase(s string) string {
	// Substitui hífens e sublinhados por espaços
	s = strings.ReplaceAll(s, "-", " ")
	s = strings.ReplaceAll(s, "_", " ")

	// Divide a string em palavras
	words := strings.Fields(s)

	// Primeira palavra em minúsculas, demais com inicial maiúscula
	for i, word := range words {
		if i == 0 {
			words[i] = strings.ToLower(word)
		} else {
			words[i] = strings.Title(strings.ToLower(word))
		}
	}

	// Junta as palavras sem espaço
	return strings.Join(words, "")
}

// ToPascalCase converte uma string em PascalCase
func ToPascalCase(s string) string {
	// Substitui hífens e sublinhados por espaços
	s = strings.ReplaceAll(s, "-", " ")
	s = strings.ReplaceAll(s, "_", " ")

	// Divide a string em palavras
	words := strings.Fields(s)

	// Todas as palavras com inicial maiúscula
	for i, word := range words {
		words[i] = strings.Title(strings.ToLower(word))
	}

	// Junta as palavras sem espaço
	return strings.Join(words, "")
}

// FormatCurrency formata um número como moeda
func FormatCurrency(value float64, currencySymbol string) string {
	return fmt.Sprintf("%s %.2f", currencySymbol, value)
}

// FormatNumber formata um número com separadores de milhar e n casas decimais
func FormatNumber(value float64, decimals int) string {
	// Implementação simplificada, deve ser adaptada para requisitos específicos
	return fmt.Sprintf("%."+strconv.Itoa(decimals)+"f", value)
}

// FormatPercentage formata um valor para string no formato de percentual
func FormatPercentage(value float64, decimals int) string {
	if decimals < 0 {
		decimals = 0
	}

	return fmt.Sprintf("%."+strconv.Itoa(decimals)+"f%%", value)
}

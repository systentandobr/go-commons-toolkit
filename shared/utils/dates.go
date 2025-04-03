package utils

import (
	"time"
)

// Common date formats
const (
	DateFormatISO8601      = "2006-01-02T15:04:05Z07:00"
	DateFormatSimple       = "2006-01-02"
	DateFormatWithTime     = "2006-01-02 15:04:05"
	DateFormatBR           = "02/01/2006"
	DateFormatBRWithTime   = "02/01/2006 15:04:05"
	DateFormatMonth        = "January 2006"
	DateFormatMonthShort   = "Jan 2006"
	DateFormatDayMonth     = "2 January"
	DateFormatDayMonthShort = "2 Jan"
	DateFormatYear         = "2006"
)

// StartOfDay retorna a data no início do dia
func StartOfDay(t time.Time) time.Time {
	return time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, t.Location())
}

// EndOfDay retorna a data no final do dia
func EndOfDay(t time.Time) time.Time {
	return time.Date(t.Year(), t.Month(), t.Day(), 23, 59, 59, 999999999, t.Location())
}

// StartOfMonth retorna a data no início do mês
func StartOfMonth(t time.Time) time.Time {
	return time.Date(t.Year(), t.Month(), 1, 0, 0, 0, 0, t.Location())
}

// EndOfMonth retorna a data no final do mês
func EndOfMonth(t time.Time) time.Time {
	return StartOfMonth(t).AddDate(0, 1, 0).Add(-time.Nanosecond)
}

// StartOfYear retorna a data no início do ano
func StartOfYear(t time.Time) time.Time {
	return time.Date(t.Year(), 1, 1, 0, 0, 0, 0, t.Location())
}

// EndOfYear retorna a data no final do ano
func EndOfYear(t time.Time) time.Time {
	return time.Date(t.Year(), 12, 31, 23, 59, 59, 999999999, t.Location())
}

// AddBusinessDays adiciona dias úteis a uma data
func AddBusinessDays(t time.Time, days int) time.Time {
	businessDays := 0
	result := t

	for businessDays < days {
		result = result.AddDate(0, 0, 1)
		if result.Weekday() != time.Saturday && result.Weekday() != time.Sunday {
			businessDays++
		}
	}

	return result
}

// FormatDate formata uma data usando um formato padrão
func FormatDate(t time.Time, format string) string {
	return t.Format(format)
}

// ParseDate analisa uma string de data no formato especificado
func ParseDate(dateStr, format string) (time.Time, error) {
	return time.Parse(format, dateStr)
}

// DateRange representa um intervalo de datas
type DateRange struct {
	Start time.Time
	End   time.Time
}

// NewDateRange cria um novo intervalo de datas
func NewDateRange(start, end time.Time) DateRange {
	return DateRange{Start: start, End: end}
}

// Contains verifica se uma data está dentro do intervalo
func (dr DateRange) Contains(date time.Time) bool {
	return (date.Equal(dr.Start) || date.After(dr.Start)) && 
	       (date.Equal(dr.End) || date.Before(dr.End))
}

// Duration retorna a duração do intervalo
func (dr DateRange) Duration() time.Duration {
	return dr.End.Sub(dr.Start)
}

// DaysIn retorna o número de dias no intervalo
func (dr DateRange) DaysIn() int {
	return int(dr.End.Sub(dr.Start).Hours() / 24)
}

// LastNDays retorna um intervalo com os últimos N dias
func LastNDays(n int) DateRange {
	end := time.Now()
	start := end.AddDate(0, 0, -n)
	return NewDateRange(start, end)
}

// LastNMonths retorna um intervalo com os últimos N meses
func LastNMonths(n int) DateRange {
	end := time.Now()
	start := end.AddDate(0, -n, 0)
	return NewDateRange(start, end)
}

// LastNYears retorna um intervalo com os últimos N anos
func LastNYears(n int) DateRange {
	end := time.Now()
	start := end.AddDate(-n, 0, 0)
	return NewDateRange(start, end)
}

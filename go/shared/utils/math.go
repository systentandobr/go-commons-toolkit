// pkg/common/utils/math.go
package utils

import (
	"math"
	"sort"
)

// RoundTo arredonda um número para n casas decimais
func RoundTo(value float64, places int) float64 {
	if places < 0 {
		places = 0
	}

	factor := math.Pow10(places)
	return math.Round(value*factor) / factor
}

// CalculateCAGR calcula a Taxa Composta de Crescimento Anual
// (Compound Annual Growth Rate)
func CalculateCAGR(initialValue, finalValue float64, years float64) float64 {
	if initialValue <= 0 || years <= 0 {
		return 0
	}

	return math.Pow(finalValue/initialValue, 1/years) - 1
}

// CalculateROI calcula o Retorno sobre o Investimento
// (Return on Investment)
func CalculateROI(initialValue, finalValue float64) float64 {
	if initialValue <= 0 {
		return 0
	}

	return (finalValue - initialValue) / initialValue
}

// CalculateStandardDeviation calcula o desvio padrão de um conjunto de valores
func CalculateStandardDeviation(values []float64) float64 {
	n := len(values)
	if n < 2 {
		return 0
	}

	// Calcular a média
	mean := CalculateMean(values)

	// Calcular a soma dos quadrados das diferenças
	sumSquaredDiffs := 0.0
	for _, v := range values {
		diff := v - mean
		sumSquaredDiffs += diff * diff
	}

	// Calcular a variância
	variance := sumSquaredDiffs / float64(n)

	// Calcular o desvio padrão
	return math.Sqrt(variance)
}

// CalculateMean calcula a média de um conjunto de valores
func CalculateMean(values []float64) float64 {
	n := len(values)
	if n == 0 {
		return 0
	}

	sum := 0.0
	for _, v := range values {
		sum += v
	}

	return sum / float64(n)
}

// CalculateMedian calcula a mediana de um conjunto de valores
func CalculateMedian(values []float64) float64 {
	n := len(values)
	if n == 0 {
		return 0
	}

	// Clonar e ordenar os valores
	sorted := make([]float64, n)
	copy(sorted, values)
	sort.Float64s(sorted)

	// Calcular a mediana
	if n%2 == 0 {
		// Número par de elementos - média dos dois do meio
		return (sorted[n/2-1] + sorted[n/2]) / 2
	}

	// Número ímpar de elementos - elemento do meio
	return sorted[n/2]
}

// CalculateVariance calcula a variância de um conjunto de valores
func CalculateVariance(values []float64) float64 {
	n := len(values)
	if n < 2 {
		return 0
	}

	// Calcular a média
	mean := CalculateMean(values)

	// Calcular a soma dos quadrados das diferenças
	sumSquaredDiffs := 0.0
	for _, v := range values {
		diff := v - mean
		sumSquaredDiffs += diff * diff
	}

	// Calcular a variância
	return sumSquaredDiffs / float64(n)
}

// CalculateCorrelation calcula o coeficiente de correlação de Pearson entre dois conjuntos de valores
func CalculateCorrelation(x, y []float64) float64 {
	n := len(x)
	if n != len(y) || n < 2 {
		return 0
	}

	// Calcular as médias
	meanX := CalculateMean(x)
	meanY := CalculateMean(y)

	// Calcular as somas necessárias
	sumXY := 0.0
	sumX2 := 0.0
	sumY2 := 0.0

	for i := 0; i < n; i++ {
		diffX := x[i] - meanX
		diffY := y[i] - meanY

		sumXY += diffX * diffY
		sumX2 += diffX * diffX
		sumY2 += diffY * diffY
	}

	// Calcular o coeficiente de correlação
	if sumX2 == 0 || sumY2 == 0 {
		return 0
	}

	return sumXY / (math.Sqrt(sumX2) * math.Sqrt(sumY2))
}

// CalculatePresentValue calcula o valor presente de um valor futuro
// (Present Value)
func CalculatePresentValue(futureValue float64, rate float64, periods int) float64 {
	if rate <= -1 {
		return 0
	}

	return futureValue / math.Pow(1+rate, float64(periods))
}

// CalculateFutureValue calcula o valor futuro de um valor presente
// (Future Value)
func CalculateFutureValue(presentValue float64, rate float64, periods int) float64 {
	return presentValue * math.Pow(1+rate, float64(periods))
}

// CalculateInternalRateOfReturn calcula a Taxa Interna de Retorno (TIR)
// usando o método de Newton-Raphson
// (Internal Rate of Return - IRR)
func CalculateInternalRateOfReturn(cashFlows []float64, guess float64, maxIterations int, tolerance float64) float64 {
	// Implementação simplificada do método de Newton-Raphson
	// Em um projeto real, pode ser necessário uma implementação mais robusta

	if len(cashFlows) < 2 {
		return 0
	}

	if maxIterations <= 0 {
		maxIterations = 100
	}

	if tolerance <= 0 {
		tolerance = 0.000001
	}

	if guess <= -1 {
		guess = 0.1
	}

	rate := guess

	for i := 0; i < maxIterations; i++ {
		// Calcular o NPV e sua derivada para a taxa atual
		npv := calculateNPV(cashFlows, rate)

		if math.Abs(npv) < tolerance {
			return rate
		}

		// Calcular a derivada
		derivative := calculateNPVDerivative(cashFlows, rate)

		if derivative == 0 {
			break
		}

		// Aplicar o método de Newton-Raphson
		newRate := rate - npv/derivative

		// Verificar convergência
		if math.Abs(newRate-rate) < tolerance {
			return newRate
		}

		rate = newRate
	}

	return rate
}

// calculateNPV calcula o Valor Presente Líquido (VPL)
// (Net Present Value - NPV)
func calculateNPV(cashFlows []float64, rate float64) float64 {
	npv := 0.0

	for i, cf := range cashFlows {
		npv += cf / math.Pow(1+rate, float64(i))
	}

	return npv
}

// calculateNPVDerivative calcula a derivada do VPL em relação à taxa
func calculateNPVDerivative(cashFlows []float64, rate float64) float64 {
	derivative := 0.0

	for i, cf := range cashFlows {
		if i > 0 {
			derivative -= float64(i) * cf / math.Pow(1+rate, float64(i+1))
		}
	}

	return derivative
}

// LinearRegression calcula a regressão linear simples
func LinearRegression(x, y []float64) (slope, intercept float64) {
	n := len(x)
	if n != len(y) || n < 2 {
		return 0, 0
	}

	// Calcular as médias
	meanX := CalculateMean(x)
	meanY := CalculateMean(y)

	// Calcular os somatórios necessários
	sumXY := 0.0
	sumX2 := 0.0

	for i := 0; i < n; i++ {
		xDiff := x[i] - meanX
		sumXY += xDiff * (y[i] - meanY)
		sumX2 += xDiff * xDiff
	}

	// Evitar divisão por zero
	if sumX2 == 0 {
		return 0, meanY
	}

	// Calcular a inclinação (slope)
	slope = sumXY / sumX2

	// Calcular a interceptação (intercept)
	intercept = meanY - slope*meanX

	return slope, intercept
}

// PredictLinearValue prediz um valor usando a equação da regressão linear
func PredictLinearValue(x float64, slope, intercept float64) float64 {
	return slope*x + intercept
}

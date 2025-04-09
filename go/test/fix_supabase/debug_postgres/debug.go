package main

import (
	"fmt"
	"os"
	"regexp"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
)

func main() {
	// Carregar variáveis de ambiente
	if _, err := os.Stat(".env"); err == nil {
		config.LoadEnv(".env")
		fmt.Println("Arquivo .env carregado")
	} else {
		fmt.Println("Arquivo .env não encontrado")
	}

	// Obter configuração
	cfg := config.Get()

	// Informações sobre a conexão PostgreSQL
	uri := cfg.Database.SupabaseURI
	fmt.Println("URI original:", uri)

	// Extrair o host da URI
	hostRaw := getHost(uri)
	fmt.Println("Host extraído pela função:", hostRaw)

	// Usar regexp para extrair o host de maneira mais robusta
	reHost := regexp.MustCompile(`postgresql://([^:]+):?(\d*)`)
	matches := reHost.FindStringSubmatch(uri)

	if len(matches) >= 2 {
		host := matches[1]
		port := "5432" // porta padrão
		if len(matches) >= 3 && matches[2] != "" {
			port = matches[2]
		}
		fmt.Printf("Host (regexp): %s, Porta: %s\n", host, port)
	} else {
		fmt.Println("Não foi possível extrair o host usando regexp")
	}

	// Montar a string de conexão completa para depuração
	fmt.Println("\nString de conexão que será usada:")
	connStr := fmt.Sprintf(
		"host=%s dbname=%s user=%s password=%s sslmode=disable",
		hostRaw,
		cfg.Database.SupabaseDatabase,
		cfg.Database.SupabaseUsername,
		cfg.Database.SupabasePassword,
	)
	fmt.Println(connStr)

	// Exibir a mensagem de erro que você está recebendo
	fmt.Println("\nErro de conexão reportado:")
	fmt.Println("dial tcp: lookup localhost:5432: no such host")
	fmt.Println("\nPossíveis soluções:")
	fmt.Println("1. Use '127.0.0.1' em vez de 'localhost'")
	fmt.Println("2. Verifique se o container do PostgreSQL está rodando")
	fmt.Println("3. Verifique o mapeamento de portas no docker-compose.yml")
	fmt.Println("4. Teste a conexão diretamente com psql ou outra ferramenta")
}

// Cópia da função getHost usada no cliente Supabase
func getHost(uri string) string {
	if len(uri) > 13 {
		return uri[13:]
	}
	return "localhost:5432"
}

package projectGenerator

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/systentandobr/toolkit/go/shared/tools"
)

func main() {
	// Definir flags de linha de comando
	projectName := flag.String("name", "", "Nome do projeto")
	description := flag.String("desc", "Um projeto Go baseado em microsserviços", "Descrição do projeto")
	modulePath := flag.String("module", "", "Caminho do módulo Go (ex: github.com/user/projeto)")
	goVersion := flag.String("goversion", "1.22", "Versão do Go")
	port := flag.Int("port", 8080, "Porta HTTP")
	outputDir := flag.String("output", ".", "Diretório de saída")
	entityName := flag.String("entity", "", "Nome da entidade principal (opcional)")
	domainName := flag.String("domain", "", "Nome do domínio da entidade (opcional)")

	flag.Parse()

	// Validar argumentos obrigatórios
	if *projectName == "" {
		fmt.Println("Erro: Nome do projeto é obrigatório (-name)")
		flag.Usage()
		os.Exit(1)
	}

	if *modulePath == "" {
		fmt.Println("Erro: Caminho do módulo é obrigatório (-module)")
		flag.Usage()
		os.Exit(1)
	}

	// Criar gerador de projetos
	generator := tools.NewProjectGenerator(*outputDir)

	// Configurar o projeto
	config := tools.ProjectConfig{
		ProjectName:       *projectName,
		Description:       *description,
		ModulePath:        *modulePath,
		GoVersion:         *goVersion,
		Port:              *port,
		RepositoryURL:     fmt.Sprintf("https://%s.git", *modulePath),
		License:           "MIT",
		EntityName:        *entityName,
		EntityDescription: "uma entidade do domínio",
		DomainName:        *domainName,
	}

	// Criar o projeto
	if err := generator.CreateMicroservice(config); err != nil {
		log.Fatalf("Erro ao criar projeto: %v", err)
	}

	// Exibir instruções
	fullPath, err := filepath.Abs(filepath.Join(*outputDir, *projectName))
	if err != nil {
		fullPath = filepath.Join(*outputDir, *projectName)
	}

	fmt.Printf("\nProjeto criado com sucesso em %s\n\n", fullPath)
	fmt.Println("Próximos passos:")
	fmt.Printf("  cd %s\n", *projectName)
	fmt.Println("  go mod tidy")
	fmt.Println("  cp .env.example .env")
	fmt.Println("  make build")
	fmt.Println("  make run")
}

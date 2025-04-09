# Como Usar o Go Commons Toolkit

Este guia mostra como utilizar o Go Commons Toolkit em seus projetos Go.

## Instalação

Para usar o toolkit em seu projeto, adicione-o como dependência:

```bash
go get github.com/systentandobr/toolkit/go
```

Ou para usar uma versão local durante o desenvolvimento, adicione um replace no seu arquivo `go.mod`:

```
replace github.com/systentandobr/toolkit/go => /caminho/absoluto/para/toolkit/go
```

## Exemplos de Uso

### 1. Configuração de Ambiente

Use o módulo de configuração para carregar variáveis de ambiente:

```go
package main

import (
	"fmt"
	"log"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
)

func main() {
	// Carregar configurações do arquivo .env
	err := config.LoadEnv(".env")
	if err != nil {
		log.Printf("Aviso: Não foi possível carregar .env: %v", err)
	}

	// Acessar configurações
	cfg := config.Get()
	fmt.Printf("Porta HTTP: %d\n", cfg.HTTPPort)
	fmt.Printf("URI do MongoDB: %s\n", cfg.MongoURI)
}
```

### 2. Cliente MongoDB

Exemplo de como usar o cliente MongoDB:

```go
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/config"
	"github.com/systentandobr/toolkit/go/shared/infrastructure/persistence/mongodb"
	"go.mongodb.org/mongo-driver/bson"
)

type User struct {
	Name  string    `bson:"name"`
	Email string    `bson:"email"`
	Date  time.Time `bson:"date"`
}

func main() {
	// Carregar configurações
	if err := config.LoadEnv(".env"); err != nil {
		log.Printf("Aviso: Não foi possível carregar .env: %v", err)
	}

	// Obter coleção
	collection, err := mongodb.NewCollection("users")
	if err != nil {
		log.Fatalf("Erro ao conectar ao MongoDB: %v", err)
	}

	// Inserir documento
	ctx := context.Background()
	user := User{
		Name:  "João Silva",
		Email: "joao@example.com",
		Date:  time.Now(),
	}

	result, err := collection.InsertOne(ctx, user)
	if err != nil {
		log.Fatalf("Erro ao inserir documento: %v", err)
	}
	fmt.Printf("Documento inserido com ID: %v\n", result.InsertedID)

	// Buscar documentos
	var users []User
	err = collection.Find(ctx, bson.M{}, &users)
	if err != nil {
		log.Fatalf("Erro ao buscar documentos: %v", err)
	}

	for _, u := range users {
		fmt.Printf("Usuário: %s (%s)\n", u.Name, u.Email)
	}
}
```

### 3. Validação de Dados

Exemplo de como usar a validação de dados:

```go
package main

import (
	"fmt"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/validation"
)

type Product struct {
	ID          string  `validate:"required"`
	Name        string  `validate:"required,min=3,max=100"`
	Description string  `validate:"max=500"`
	Price       float64 `validate:"required,gt=0"`
	Stock       int     `validate:"min=0"`
}

func main() {
	product := Product{
		ID:          "",               // Inválido: required
		Name:        "A",              // Inválido: min=3
		Description: "Um produto",
		Price:       -10,              // Inválido: gt=0
		Stock:       -5,               // Inválido: min=0
	}

	errors, valid := validation.ValidateStruct(product)
	if !valid {
		fmt.Println("Erros de validação:")
		for _, err := range errors {
			fmt.Printf("- Campo %s: %s\n", err.Field, err.Message)
		}
	} else {
		fmt.Println("Produto válido")
	}
}
```

### 4. JWT e Autenticação

Exemplo de como usar o JWT para autenticação:

```go
package main

import (
	"fmt"
	"time"

	"github.com/systentandobr/toolkit/go/shared/security"
)

func main() {
	// Configurar serviço JWT
	jwtConfig := security.JWTConfig{
		SecretKey:             "chave-secreta-para-desenvolvimento",
		AccessTokenExpiration: 15 * time.Minute,
		RefreshTokenExpiration: 7 * 24 * time.Hour,
		Issuer:                "meu-servico",
	}
	
	jwtService := security.NewJWTService(jwtConfig)
	
	// Gerar tokens
	token, err := jwtService.GenerateTokens(
		"user-123",             // ID do usuário
		"joao.silva",           // Nome de usuário
		"joao@example.com",     // Email
		[]string{"user"},       // Roles/funções
		map[string]interface{}{ // Metadados adicionais
			"empresa": "Acme Inc",
			"plano": "premium",
		},
	)
	
	if err != nil {
		fmt.Printf("Erro ao gerar token: %v\n", err)
		return
	}
	
	fmt.Printf("Access Token: %s\n", token.AccessToken)
	fmt.Printf("Refresh Token: %s\n", token.RefreshToken)
	fmt.Printf("Expira em: %v\n", token.ExpiresAt)
	
	// Validar token
	claims, err := jwtService.ValidateToken(token.AccessToken)
	if err != nil {
		fmt.Printf("Erro ao validar token: %v\n", err)
		return
	}
	
	fmt.Printf("Token validado para usuário: %s\n", claims.Username)
	fmt.Printf("Roles: %v\n", claims.Roles)
}
```

### 5. Cliente HTTP

Exemplo de como usar o cliente HTTP:

```go
package main

import (
	"context"
	"fmt"
	"time"

	"github.com/systentandobr/toolkit/go/shared/infrastructure/http"
)

type Post struct {
	ID     int    `json:"id"`
	Title  string `json:"title"`
	Body   string `json:"body"`
	UserID int    `json:"userId"`
}

func main() {
	// Criar cliente HTTP com opções
	client := http.NewClient(
		http.WithBaseURL("https://jsonplaceholder.typicode.com"),
		http.WithTimeout(10*time.Second),
		http.WithHeader("Accept", "application/json"),
	)
	
	// Criar contexto
	ctx := context.Background()
	
	// Buscar posts
	var posts []Post
	err := client.Get(ctx, "/posts", &posts)
	if err != nil {
		fmt.Printf("Erro ao buscar posts: %v\n", err)
		return
	}
	
	fmt.Printf("Encontrados %d posts\n", len(posts))
	
	// Buscar um post específico
	var post Post
	err = client.Get(ctx, "/posts/1", &post)
	if err != nil {
		fmt.Printf("Erro ao buscar post: %v\n", err)
		return
	}
	
	fmt.Printf("Post: %s\n", post.Title)
	
	// Criar um novo post
	newPost := Post{
		Title:  "Novo Post",
		Body:   "Conteúdo do novo post",
		UserID: 1,
	}
	
	var createdPost Post
	err = client.Post(ctx, "/posts", newPost, &createdPost)
	if err != nil {
		fmt.Printf("Erro ao criar post: %v\n", err)
		return
	}
	
	fmt.Printf("Post criado com ID: %d\n", createdPost.ID)
}
```

### 6. Geração de Projetos

Você pode criar novos projetos usando o gerador de projetos:

```bash
cd $GOPATH/src/github.com/systentandobr/toolkit/go
go run cmd/examples/project-generator/main.go \
  -name meu-servico \
  -module github.com/meu-usuario/meu-servico \
  -desc "Descrição do serviço" \
  -entity Usuario \
  -domain usuario
```

## Usando com Docker Compose

O toolkit inclui exemplos de Docker Compose para facilitar o desenvolvimento:

```yaml
# docker-compose.yml do seu projeto
version: '3.8'

services:
  app:
    build: .
    depends_on:
      - mongodb
      - kafka
    environment:
      - MONGO_URI=mongodb://mongodb:27017
      - KAFKA_BOOTSTRAP_SERVER=kafka:9092

  # Você pode incluir os serviços necessários do docker-compose do toolkit
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  # Outros serviços...

volumes:
  mongodb_data:
```

## Integração com Frameworks Web

### Exemplo com Echo

```go
package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/systentandobr/toolkit/go/shared/infrastructure/validation"
	"github.com/systentandobr/toolkit/go/shared/security"
)

type LoginRequest struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required,min=6"`
}

func main() {
	// Criar instância do Echo
	e := echo.New()

	// Configurar JWT
	jwtConfig := security.DefaultJWTConfig()
	jwtService := security.NewJWTService(jwtConfig)

	// Endpoint de login
	e.POST("/login", func(c echo.Context) error {
		var req LoginRequest
		if err := c.Bind(&req); err != nil {
			return c.JSON(http.StatusBadRequest, map[string]string{
				"error": "Formato de requisição inválido",
			})
		}

		// Validar requisição
		errors, valid := validation.ValidateStruct(req)
		if !valid {
			return c.JSON(http.StatusBadRequest, map[string]interface{}{
				"error":   "Erro de validação",
				"details": errors,
			})
		}

		// Autenticar usuário (exemplo simplificado)
		if req.Email != "admin@example.com" || req.Password != "123456" {
			return c.JSON(http.StatusUnauthorized, map[string]string{
				"error": "Credenciais inválidas",
			})
		}

		// Gerar token
		token, err := jwtService.GenerateTokens(
			"user-123",
			"admin",
			req.Email,
			[]string{"admin"},
			nil,
		)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, map[string]string{
				"error": "Erro ao gerar token",
			})
		}

		return c.JSON(http.StatusOK, token)
	})

	// Iniciar servidor
	e.Start(":8080")
}
```

## Próximos Passos

1. Consulte a documentação completa dos componentes na pasta `docs/`
2. Explore os exemplos na pasta `cmd/examples/`
3. Personalize o toolkit conforme suas necessidades

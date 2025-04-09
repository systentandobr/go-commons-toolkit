# Go Commons Toolkit

O Go Commons Toolkit é uma biblioteca para aplicações Go, fornecendo componentes e utilitários reutilizáveis para diferentes projetos. Ele implementa padrões comuns e reduz o esforço de desenvolvimento, permitindo que as equipes se concentrem na lógica de negócios.

## Componentes

### Infraestrutura

- **Config**: Gerenciamento de configurações baseado em variáveis de ambiente
- **Persistence**: Clientes para MongoDB e Supabase/PostgreSQL
- **HTTP**: Cliente e utilitários HTTP, middleware e respostas padronizadas
- **Messaging**: Cliente para Apache Kafka (producer/consumer)
- **Validation**: Validação de dados e requisições

### Segurança

- **Auth**: Autenticação JWT e gerenciamento de senhas
- **Middleware**: Camadas de autorização e CORS para APIs

### Ferramentas

- **SchemaGenerator**: Geração de código e esquemas
- **ProjectGenerator**: Criação de estrutura de projetos
- **DBMigrator**: Gerenciamento de migrações de banco de dados

### Utilitários

- **Errors**: Gerenciamento padronizado de erros
- **Dates**: Manipulação e formatação de datas
- **Strings**: Manipulação de strings e formatação

## Instalação

```bash
go get github.com/systentandobr/toolkit/go
```

## Uso

```go
import "github.com/systentandobr/toolkit/go"
```

## Variáveis de Ambiente

O toolkit usa as seguintes variáveis de ambiente:

- `MONGO_URI`: URI de conexão com MongoDB
- `MONGO_DATABASE_NAME`: Nome do banco de dados MongoDB
- `KAFKA_BOOTSTRAP_SERVER`: Servidor(es) Kafka
- `KAFKA_CONSUMER_GROUP_ID`: ID do grupo de consumidor Kafka
- `SUPABASE_URI`: URI de conexão com Supabase/PostgreSQL
- `SUPABASE_DATABASE`: Nome do banco de dados PostgreSQL
- `SUPABASE_USERNAME`: Usuário do banco de dados PostgreSQL
- `SUPABASE_PASSWORD`: Senha do banco de dados PostgreSQL

## Exemplos

Veja a pasta `cmd/examples` para exemplos completos de uso dos componentes:

- **MongoDB**: Exemplo de uso do cliente MongoDB
- **Supabase**: Exemplo de uso do cliente Supabase/PostgreSQL
- **Kafka**: Exemplos de produtor e consumidor Kafka
- **HTTP**: Exemplo de API com validação e autenticação
- **Project Generator**: Exemplo de geração de projetos

## Geração de Projetos

O toolkit inclui um gerador de projetos para criar rapidamente microsserviços:

```bash
go run cmd/examples/project-generator/main.go -name meu-servico -module github.com/usuario/meu-servico -entity Usuario -domain usuario
```

## Desenvolvimento

### Requisitos

- Go 1.22 ou superior
- Docker (para testes)

### Configuração

```bash
# Clonar o repositório
git clone https://github.com/systentandobr/toolkit/go.git
cd toolkit/go

# Criar arquivo .env
cp .env.example .env

# Instalar dependências
go mod download
go mod tidy

# Executar testes
make test
```

### Ambiente Docker

O toolkit inclui um arquivo `docker-compose.yml` com todos os serviços necessários para desenvolvimento:

```bash
# Iniciar os serviços
make docker-up

# Parar os serviços
make docker-down
```

## Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie um novo Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

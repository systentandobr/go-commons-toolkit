# Systentando Toolkit para Rust - Guia de Uso

Este documento descreve como utilizar o toolkit de desenvolvimento Rust no ecossistema Systentando.

## Instalação

Para instalar o toolkit como dependência do seu projeto, adicione ao seu `Cargo.toml`:

```toml
[dependencies]
systentando-toolkit = "0.1.0"
```

Para utilizar as ferramentas CLI, instale globalmente:

```bash
cargo install systentando-toolkit
```

## Utilizando a CLI

### Criar um novo projeto

```bash
# Criar um serviço HTTP básico
systentando new http-service meu-servico

# Criar um consumidor Kafka
systentando new kafka-consumer meu-consumidor

# Criar uma biblioteca
systentando new library minha-lib

# Opções adicionais
systentando new http-service meu-servico --with-database --with-telemetry --with-docker
```

### Outras ferramentas CLI

```bash
# Gerar um novo handler para serviço HTTP
systentando generate handler usuario

# Gerar um novo módulo de banco de dados
systentando generate repository usuario

# Gerar um novo consumidor Kafka
systentando generate consumer pedidos
```

## Utilizando a biblioteca nos seus projetos

### Configuração e Logging

```rust
use systentando_toolkit::prelude::*;

// Carregar configuração
let config = Config::load()?;

// Inicializar logs
Logger::init(&config)?;

// Inicializar telemetria se configurada
if let Some(telemetry_config) = &config.telemetry {
    if telemetry_config.enabled {
        Telemetry::init(&config)?;
    }
}
```

### Tratamento de Erros

```rust
use systentando_toolkit::prelude::*;

// Criar um erro específico
let error = AppError::not_found("Usuário não encontrado")
    .with_context(json!({ "user_id": "123" }));

// Em um handler HTTP, retornar o erro
fn get_user(id: String) -> Result<HttpResponse, AppError> {
    let user = find_user(&id).ok_or_else(|| 
        AppError::not_found("Usuário não encontrado")
    )?;
    
    Ok(HttpResponse::Ok().json(user))
}
```

### Banco de Dados

```rust
use systentando_toolkit::prelude::*;
use systentando_toolkit::db::postgres::PgDatabase;

// Conectar ao banco de dados
let db = PgDatabase::connect(&config.database.unwrap()).await?;

// Executar query
let users = db.query("SELECT * FROM users").await?;
```

### Servidor Web

```rust
use systentando_toolkit::prelude::*;
use systentando_toolkit::web::{Server, Router};

// Criar servidor
let server = Server::new(&config)
    .with_logging()
    .with_cors()
    .with_json();

// Definir rotas
let router = Router::new()
    .get("/health", health_handler)
    .scope("/api/v1", api_v1_routes);

// Iniciar servidor
server.run(router).await?;
```

## Melhores Práticas

### Estrutura de Diretórios Recomendada

```
.
├── config/
│   ├── default.example.toml
│   └── default.toml
├── src/
│   ├── config.rs
│   ├── error.rs
│   ├── handlers/
│   ├── main.rs
│   ├── models/
│   ├── repositories/
│   └── routes.rs
├── tests/
├── Cargo.toml
├── Dockerfile
└── README.md
```

### Convenções de Código

- Use `snake_case` para nomes de variáveis, funções e módulos
- Use `CamelCase` para tipos, traits e enums
- Use `SCREAMING_SNAKE_CASE` para constantes
- Documente todas as funções e módulos públicos com comentários `///`
- Use `Result<T, Error>` para funções que podem falhar
- Utilize o tipo `AppError` para erros de aplicação

### Prática de Teste

- Teste todas as funções públicas
- Use mocks para dependências externas
- Separe testes de unidade e integração
- Nomeie testes com o prefixo `test_` e uma descrição clara

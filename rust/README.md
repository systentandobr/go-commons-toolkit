# Systentando Toolkit para Rust

Este toolkit fornece componentes, bibliotecas e utilitários para desenvolvimento de microsserviços em Rust dentro do ecossistema Systentando.

## Recursos

- **Configuração** - Carregamento e validação de configuração a partir de arquivos e variáveis de ambiente
- **Logs e Telemetria** - Integração com tracing e OpenTelemetry
- **Web Framework** - Módulos base para Actix Web com middleware comum
- **Banco de Dados** - Abstrações para acesso a banco de dados com SQLx
- **Cliente HTTP** - Cliente HTTP com circuit breaker, retry e logging
- **CLI** - Ferramentas de linha de comando para geração de projetos
- **Validação** - Componentes para validação de dados de entrada
- **Erros** - Sistema padronizado para tratamento de erros
- **Segurança** - Módulos para autenticação e autorização

## Começando

### Instalação

Adicione o toolkit como dependência no seu `Cargo.toml`:

```toml
[dependencies]
systentando-toolkit = "0.1.0"
```

### Exemplo Básico

```rust
use systentando_toolkit::prelude::*;
use systentando_toolkit::web::{Server, Router};

#[tokio::main]
async fn main() -> Result<()> {
    // Inicializar configuração e logs
    let config = Config::load()?;
    Logger::init(&config)?;
    
    // Criar servidor
    let server = Server::new(&config)
        .with_cors()
        .with_metrics()
        .with_request_logging();
    
    // Definir rotas
    let router = Router::new()
        .add_get("/health", health_handler);
    
    // Iniciar servidor
    server.run(router).await?;
    
    Ok(())
}

async fn health_handler() -> HttpResponse {
    HttpResponse::Ok().json(json!({ "status": "ok" }))
}
```

## Módulos

- **config** - Carregamento e validação de configuração
- **logging** - Sistema de logging e tracing
- **telemetry** - Exportação de métricas e traços
- **web** - Componentes para servidores web
- **db** - Acesso a banco de dados
- **http** - Cliente HTTP
- **validation** - Validação de dados
- **error** - Tratamento de erros
- **security** - Autenticação e autorização
- **cli** - Ferramentas de linha de comando

## Exemplos

Consulte a pasta `examples/` para exemplos completos de uso.

## Licença

Este projeto está licenciado sob a [Licença MIT](../LICENSE).

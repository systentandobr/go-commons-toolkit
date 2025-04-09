/*!
 * # Systentando Toolkit
 * 
 * Um toolkit para desenvolvimento de microsserviços em Rust dentro do ecossistema Systentando.
 * 
 * ## Características
 * 
 * - Configuração fácil a partir de arquivos e variáveis de ambiente
 * - Logging estruturado e telemetria
 * - Framework web com middleware comum
 * - Abstrações para acesso a banco de dados
 * - Cliente HTTP resiliente
 * - Tratamento padronizado de erros
 * - Utilitários para validação
 * 
 * ## Exemplo básico
 * 
 * ```rust,no_run
 * use systentando_toolkit::prelude::*;
 * use systentando_toolkit::web::{Server, Router};
 * 
 * #[tokio::main]
 * async fn main() -> Result<()> {
 *     // Inicializar configuração e logs
 *     let config = Config::load()?;
 *     Logger::init(&config)?;
 *     
 *     // Criar servidor
 *     let server = Server::new(&config)
 *         .with_cors()
 *         .with_metrics()
 *         .with_request_logging();
 *     
 *     // Definir rotas
 *     let router = Router::new()
 *         .add_get("/health", health_handler);
 *     
 *     // Iniciar servidor
 *     server.run(router).await?;
 *     
 *     Ok(())
 * }
 * 
 * async fn health_handler() -> HttpResponse {
 *     HttpResponse::Ok().json(json!({ "status": "ok" }))
 * }
 * ```
 */

// Reexporta dependências comuns
pub use anyhow::{Result, Error, anyhow};
pub use chrono;
pub use serde::{Serialize, Deserialize};
pub use serde_json::{json, Value};
pub use uuid::Uuid;
pub use validator::{Validate, ValidationError};

// Módulos do toolkit
pub mod config;
pub mod logging;
pub mod telemetry;
pub mod web;
pub mod db;
pub mod http;
pub mod error;
pub mod validation;
pub mod security;
pub mod util;

/// Prelude para importar todos os tipos e traits comuns
pub mod prelude {
    pub use crate::{Result, Error, anyhow};
    pub use crate::config::Config;
    pub use crate::logging::{Logger, log};
    pub use crate::telemetry::Telemetry;
    pub use crate::web::{Server, Router, HttpResponse, HttpRequest};
    pub use crate::db::{Database, Repository, Entity};
    pub use crate::http::Client;
    pub use crate::error::{AppError, ErrorResponse, ErrorKind};
    pub use crate::validation::Validator;
    pub use crate::security::{Auth, Claims, Role};
    pub use crate::util::*;
    
    // Reexporta tipos comuns
    pub use serde::{Serialize, Deserialize};
    pub use serde_json::{json, Value};
    pub use uuid::Uuid;
    pub use validator::Validate;
    pub use chrono::{DateTime, Utc};
}

/// Versão do toolkit
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Initialize the toolkit with default configuration
pub fn init() -> Result<()> {
    let config = config::Config::load()?;
    logging::Logger::init(&config)?;
    telemetry::Telemetry::init(&config)?;
    
    Ok(())
}

/// Shutdown the toolkit gracefully
pub async fn shutdown() -> Result<()> {
    telemetry::Telemetry::shutdown().await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
    }
}

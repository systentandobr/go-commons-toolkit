//! Módulo para carregamento e validação de configuração
//!
//! Este módulo permite carregar configurações a partir de arquivos e variáveis
//! de ambiente, combinando-os de acordo com a prioridade definida.

use anyhow::{Result, anyhow};
use config::{Config as ConfigSource, Environment, File};
use serde::{Deserialize, Serialize};
use std::env;
use std::path::Path;

/// Environments suportados pela aplicação
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Environment {
    /// Ambiente de desenvolvimento local
    Development,
    /// Ambiente de testes
    Test,
    /// Ambiente de staging (pré-produção)
    Staging,
    /// Ambiente de produção
    Production,
}

impl Default for Environment {
    fn default() -> Self {
        Environment::Development
    }
}

impl std::fmt::Display for Environment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Environment::Development => write!(f, "development"),
            Environment::Test => write!(f, "test"),
            Environment::Staging => write!(f, "staging"),
            Environment::Production => write!(f, "production"),
        }
    }
}

impl std::str::FromStr for Environment {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "development" | "dev" => Ok(Environment::Development),
            "test" => Ok(Environment::Test),
            "staging" | "stage" => Ok(Environment::Staging),
            "production" | "prod" => Ok(Environment::Production),
            _ => Err(anyhow!("Invalid environment: {}", s)),
        }
    }
}

/// Níveis de log suportados
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum LogLevel {
    /// Nível de trace (mais detalhado)
    Trace,
    /// Nível de debug
    Debug,
    /// Nível de informação
    Info,
    /// Nível de aviso
    Warn,
    /// Nível de erro
    Error,
}

impl Default for LogLevel {
    fn default() -> Self {
        LogLevel::Info
    }
}

impl std::fmt::Display for LogLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LogLevel::Trace => write!(f, "trace"),
            LogLevel::Debug => write!(f, "debug"),
            LogLevel::Info => write!(f, "info"),
            LogLevel::Warn => write!(f, "warn"),
            LogLevel::Error => write!(f, "error"),
        }
    }
}

impl std::str::FromStr for LogLevel {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "trace" => Ok(LogLevel::Trace),
            "debug" => Ok(LogLevel::Debug),
            "info" => Ok(LogLevel::Info),
            "warn" => Ok(LogLevel::Warn),
            "error" => Ok(LogLevel::Error),
            _ => Err(anyhow!("Invalid log level: {}", s)),
        }
    }
}

/// Configuração para telemetria
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryConfig {
    /// Se a telemetria está habilitada
    #[serde(default)]
    pub enabled: bool,
    /// Endpoint do coletor OTLP
    #[serde(default = "default_telemetry_endpoint")]
    pub endpoint: String,
    /// Nome do serviço para telemetria
    pub service_name: String,
}

fn default_telemetry_endpoint() -> String {
    "http://localhost:4318".to_string()
}

/// Configuração para banco de dados
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    /// URL de conexão com o banco de dados
    pub url: String,
    /// Número máximo de conexões no pool
    #[serde(default = "default_max_connections")]
    pub max_connections: u32,
    /// Tempo máximo de espera por conexão (em segundos)
    #[serde(default = "default_connection_timeout")]
    pub connection_timeout: u64,
}

fn default_max_connections() -> u32 {
    10
}

fn default_connection_timeout() -> u64 {
    30
}

/// Configuração para o servidor HTTP
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    /// Host para bind do servidor
    #[serde(default = "default_host")]
    pub host: String,
    /// Porta para bind do servidor
    #[serde(default = "default_port")]
    pub port: u16,
    /// Timeout para requisições (em segundos)
    #[serde(default = "default_request_timeout")]
    pub request_timeout: u64,
}

fn default_host() -> String {
    "0.0.0.0".to_string()
}

fn default_port() -> u16 {
    8080
}

fn default_request_timeout() -> u64 {
    30
}

/// Configuração principal da aplicação
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Nome do serviço
    pub service_name: String,
    /// Ambiente atual
    #[serde(default)]
    pub environment: Environment,
    /// Nível de log
    #[serde(default)]
    pub log_level: LogLevel,
    /// Configuração de telemetria
    #[serde(default)]
    pub telemetry: Option<TelemetryConfig>,
    /// Configuração do servidor
    #[serde(default)]
    pub server: Option<ServerConfig>,
    /// Configuração de banco de dados
    #[serde(default)]
    pub database: Option<DatabaseConfig>,
}

impl Config {
    /// Carrega a configuração a partir de arquivos e variáveis de ambiente
    pub fn load() -> Result<Self> {
        // Detectar ambiente
        let environment = env::var("ENVIRONMENT")
            .or_else(|_| env::var("RUST_ENV"))
            .unwrap_or_else(|_| "development".to_string())
            .parse::<Environment>()?;

        // Construir fonte de configuração
        let mut builder = ConfigSource::builder();

        // Carregar arquivo de configuração padrão se existir
        if Path::new("config/default.toml").exists() {
            builder = builder.add_source(File::with_name("config/default"));
        }

        // Carregar arquivo específico do ambiente se existir
        let env_config = format!("config/{}", environment.to_string());
        if Path::new(&format!("{}.toml", env_config)).exists() {
            builder = builder.add_source(File::with_name(&env_config));
        }

        // Carregar arquivo .env local se existir
        if Path::new(".env").exists() {
            dotenv::dotenv().ok();
        }

        // Carregar variáveis de ambiente
        builder = builder.add_source(
            Environment::with_prefix("APP")
                .separator("__")
                .keep_prefix(false),
        );

        // Construir configuração
        let config: Config = builder.build()?.try_deserialize()?;

        // Adicionar nome do serviço à configuração de telemetria se não definido
        let mut config = config;
        if let Some(telemetry) = &mut config.telemetry {
            if telemetry.service_name.is_empty() {
                telemetry.service_name = config.service_name.clone();
            }
        }

        Ok(config)
    }

    /// Obtém a URL do servidor
    pub fn server_url(&self) -> String {
        let server = self.server.as_ref().unwrap_or_else(|| {
            // Usar valores padrão se não configurado
            &ServerConfig {
                host: default_host(),
                port: default_port(),
                request_timeout: default_request_timeout(),
            }
        });

        format!("http://{}:{}", server.host, server.port)
    }

    /// Verifica se é ambiente de desenvolvimento
    pub fn is_development(&self) -> bool {
        self.environment == Environment::Development
    }

    /// Verifica se é ambiente de produção
    pub fn is_production(&self) -> bool {
        self.environment == Environment::Production
    }
}

impl Default for Config {
    fn default() -> Self {
        Config {
            service_name: "unknown-service".to_string(),
            environment: Environment::default(),
            log_level: LogLevel::default(),
            telemetry: None,
            server: None,
            database: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_environment_parsing() {
        assert_eq!(
            "development".parse::<Environment>().unwrap(),
            Environment::Development
        );
        assert_eq!("dev".parse::<Environment>().unwrap(), Environment::Development);
        assert_eq!("test".parse::<Environment>().unwrap(), Environment::Test);
        assert_eq!(
            "production".parse::<Environment>().unwrap(),
            Environment::Production
        );
        assert_eq!("prod".parse::<Environment>().unwrap(), Environment::Production);

        assert!("invalid".parse::<Environment>().is_err());
    }

    #[test]
    fn test_log_level_parsing() {
        assert_eq!("trace".parse::<LogLevel>().unwrap(), LogLevel::Trace);
        assert_eq!("debug".parse::<LogLevel>().unwrap(), LogLevel::Debug);
        assert_eq!("info".parse::<LogLevel>().unwrap(), LogLevel::Info);
        assert_eq!("warn".parse::<LogLevel>().unwrap(), LogLevel::Warn);
        assert_eq!("error".parse::<LogLevel>().unwrap(), LogLevel::Error);

        assert!("invalid".parse::<LogLevel>().is_err());
    }

    #[test]
    fn test_config_defaults() {
        let config = Config::default();
        assert_eq!(config.service_name, "unknown-service");
        assert_eq!(config.environment, Environment::Development);
        assert_eq!(config.log_level, LogLevel::Info);
        assert!(config.telemetry.is_none());
        assert!(config.server.is_none());
        assert!(config.database.is_none());
    }
}

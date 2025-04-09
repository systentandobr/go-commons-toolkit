//! Configuração da aplicação

use anyhow::{Result, Context};
use config::{Config as ConfigSource, Environment, File};
use serde::{Deserialize, Serialize};
use std::env;
use std::path::Path;
use systentando_toolkit::config::{Environment as AppEnv, LogLevel, TelemetryConfig, ServerConfig, DatabaseConfig};

/// Configuração principal da aplicação
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Nome do serviço
    pub service_name: String,
    
    /// Ambiente atual
    #[serde(default)]
    pub environment: AppEnv,
    
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
            .parse::<AppEnv>()?;

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
        let config: Config = builder.build()
            .context("Falha ao construir configuração")?
            .try_deserialize()
            .context("Falha ao deserializar configuração")?;

        // Adicionar nome do serviço à configuração de telemetria se não definido
        let mut config = config;
        if let Some(telemetry) = &mut config.telemetry {
            if telemetry.service_name.is_empty() {
                telemetry.service_name = config.service_name.clone();
            }
        }

        Ok(config)
    }
}

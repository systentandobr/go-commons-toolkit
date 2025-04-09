// Template para arquivo config/default.example.toml
pub const DEFAULT_CONFIG_TEMPLATE: &str = r#"# Configuração do serviço
service_name = "{{app_name}}"
environment = "development"  # development, test, staging, production
log_level = "debug"  # trace, debug, info, warn, error

# Configuração do servidor HTTP
[server]
host = "0.0.0.0"
port = 8080
request_timeout = 30  # segundos

{{database_config}}

{{telemetry_config}}
"#;

// Template para configuração de banco de dados
pub const DATABASE_CONFIG_TEMPLATE: &str = r#"
# Configuração do banco de dados
[database]
url = "postgres://postgres:postgres@localhost:5432/{{app_name}}"
max_connections = 10
connection_timeout = 30  # segundos
"#;

// Template para configuração de telemetria
pub const TELEMETRY_CONFIG_TEMPLATE: &str = r#"
# Configuração de telemetria
[telemetry]
enabled = true
endpoint = "http://localhost:4318"  # Endpoint OTLP HTTP
service_name = "{{app_name}}"
"#;

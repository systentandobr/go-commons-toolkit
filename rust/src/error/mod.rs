//! Módulo para tratamento unificado de erros
//!
//! Fornece tipos para representar erros de aplicação de forma consistente,
//! além de integração com APIs web para respostas de erro padronizadas.

use serde::{Deserialize, Serialize};
use std::fmt;
use thiserror::Error;

/// Tipos de erro da aplicação
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ErrorKind {
    /// Erro de validação de dados
    ValidationError,
    /// Erro de autenticação (não autenticado)
    AuthenticationError,
    /// Erro de autorização (sem permissão)
    AuthorizationError,
    /// Recurso não encontrado
    NotFoundError,
    /// Conflito (ex: recurso já existe)
    ConflictError,
    /// Erro em serviço externo
    ExternalServiceError,
    /// Erro interno do servidor
    InternalError,
    /// Erro de banco de dados
    DatabaseError,
    /// Erro de configuração
    ConfigurationError,
    /// Limite de taxa excedido
    RateLimitError,
    /// Solicitação inválida
    BadRequestError,
}

impl ErrorKind {
    /// Obtém o código HTTP associado ao tipo de erro
    pub fn status_code(&self) -> u16 {
        match self {
            ErrorKind::ValidationError => 400,
            ErrorKind::AuthenticationError => 401,
            ErrorKind::AuthorizationError => 403,
            ErrorKind::NotFoundError => 404,
            ErrorKind::ConflictError => 409,
            ErrorKind::ExternalServiceError => 502,
            ErrorKind::InternalError => 500,
            ErrorKind::DatabaseError => 500,
            ErrorKind::ConfigurationError => 500,
            ErrorKind::RateLimitError => 429,
            ErrorKind::BadRequestError => 400,
        }
    }

    /// Verifica se o erro é operacional (esperado durante a operação normal)
    pub fn is_operational(&self) -> bool {
        match self {
            ErrorKind::ValidationError
            | ErrorKind::AuthenticationError
            | ErrorKind::AuthorizationError
            | ErrorKind::NotFoundError
            | ErrorKind::ConflictError
            | ErrorKind::RateLimitError
            | ErrorKind::BadRequestError => true,
            
            ErrorKind::ExternalServiceError
            | ErrorKind::InternalError
            | ErrorKind::DatabaseError
            | ErrorKind::ConfigurationError => false,
        }
    }
}

impl fmt::Display for ErrorKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorKind::ValidationError => write!(f, "VALIDATION_ERROR"),
            ErrorKind::AuthenticationError => write!(f, "AUTHENTICATION_ERROR"),
            ErrorKind::AuthorizationError => write!(f, "AUTHORIZATION_ERROR"),
            ErrorKind::NotFoundError => write!(f, "NOT_FOUND_ERROR"),
            ErrorKind::ConflictError => write!(f, "CONFLICT_ERROR"),
            ErrorKind::ExternalServiceError => write!(f, "EXTERNAL_SERVICE_ERROR"),
            ErrorKind::InternalError => write!(f, "INTERNAL_ERROR"),
            ErrorKind::DatabaseError => write!(f, "DATABASE_ERROR"),
            ErrorKind::ConfigurationError => write!(f, "CONFIGURATION_ERROR"),
            ErrorKind::RateLimitError => write!(f, "RATE_LIMIT_ERROR"),
            ErrorKind::BadRequestError => write!(f, "BAD_REQUEST_ERROR"),
        }
    }
}

/// Erro de aplicação
#[derive(Error, Debug)]
pub struct AppError {
    /// Tipo de erro
    pub kind: ErrorKind,
    /// Mensagem de erro
    pub message: String,
    /// Contexto adicional (opcional)
    pub context: Option<serde_json::Value>,
    /// Erro original que causou este erro (opcional)
    pub source: Option<Box<dyn std::error::Error + Send + Sync>>,
}

impl AppError {
    /// Cria um novo erro de aplicação
    pub fn new<S: Into<String>>(kind: ErrorKind, message: S) -> Self {
        Self {
            kind,
            message: message.into(),
            context: None,
            source: None,
        }
    }

    /// Adiciona contexto ao erro
    pub fn with_context<T: Serialize>(mut self, context: T) -> Self {
        if let Ok(json) = serde_json::to_value(context) {
            self.context = Some(json);
        }
        self
    }

    /// Adiciona a causa original do erro
    pub fn with_source<E: std::error::Error + Send + Sync + 'static>(mut self, source: E) -> Self {
        self.source = Some(Box::new(source));
        self
    }

    /// Converte para resposta HTTP
    pub fn to_response(&self) -> ErrorResponse {
        ErrorResponse {
            error: ErrorDetail {
                kind: self.kind,
                message: self.message.clone(),
                context: self.context.clone(),
            },
        }
    }

    /// Obtém o código HTTP associado ao erro
    pub fn status_code(&self) -> u16 {
        self.kind.status_code()
    }

    /// Verifica se o erro é operacional
    pub fn is_operational(&self) -> bool {
        self.kind.is_operational()
    }

    // Métodos auxiliares para criar erros específicos
    
    /// Cria um erro de validação
    pub fn validation<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::ValidationError, message)
    }

    /// Cria um erro de autenticação
    pub fn authentication<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::AuthenticationError, message)
    }

    /// Cria um erro de autorização
    pub fn authorization<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::AuthorizationError, message)
    }

    /// Cria um erro de recurso não encontrado
    pub fn not_found<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::NotFoundError, message)
    }

    /// Cria um erro de conflito
    pub fn conflict<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::ConflictError, message)
    }

    /// Cria um erro de serviço externo
    pub fn external_service<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::ExternalServiceError, message)
    }

    /// Cria um erro interno
    pub fn internal<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::InternalError, message)
    }

    /// Cria um erro de banco de dados
    pub fn database<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::DatabaseError, message)
    }

    /// Cria um erro de configuração
    pub fn configuration<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::ConfigurationError, message)
    }

    /// Cria um erro de limite de taxa excedido
    pub fn rate_limit<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::RateLimitError, message)
    }

    /// Cria um erro de solicitação inválida
    pub fn bad_request<S: Into<String>>(message: S) -> Self {
        Self::new(ErrorKind::BadRequestError, message)
    }
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.kind, self.message)
    }
}

/// Detalhes do erro para resposta ao cliente
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorDetail {
    /// Tipo de erro
    pub kind: ErrorKind,
    /// Mensagem de erro
    pub message: String,
    /// Contexto adicional (opcional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub context: Option<serde_json::Value>,
}

/// Resposta de erro para API
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorResponse {
    /// Detalhes do erro
    pub error: ErrorDetail,
}

/// Conversão de erros anyhow para AppError
impl From<anyhow::Error> for AppError {
    fn from(error: anyhow::Error) -> Self {
        // Se já for um AppError, retornar diretamente
        if let Some(app_error) = error.downcast_ref::<AppError>() {
            return app_error.clone();
        }

        // Caso contrário, criar um erro interno genérico
        Self::new(
            ErrorKind::InternalError,
            format!("Erro interno: {}", error),
        )
        .with_source(error)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_kind_status_codes() {
        assert_eq!(ErrorKind::ValidationError.status_code(), 400);
        assert_eq!(ErrorKind::AuthenticationError.status_code(), 401);
        assert_eq!(ErrorKind::AuthorizationError.status_code(), 403);
        assert_eq!(ErrorKind::NotFoundError.status_code(), 404);
        assert_eq!(ErrorKind::ConflictError.status_code(), 409);
        assert_eq!(ErrorKind::RateLimitError.status_code(), 429);
        assert_eq!(ErrorKind::ExternalServiceError.status_code(), 502);
        assert_eq!(ErrorKind::InternalError.status_code(), 500);
        assert_eq!(ErrorKind::DatabaseError.status_code(), 500);
        assert_eq!(ErrorKind::ConfigurationError.status_code(), 500);
        assert_eq!(ErrorKind::BadRequestError.status_code(), 400);
    }

    #[test]
    fn test_app_error_creation() {
        let error = AppError::validation("Campo inválido")
            .with_context(serde_json::json!({
                "field": "email",
                "reason": "formato inválido"
            }));

        assert_eq!(error.kind, ErrorKind::ValidationError);
        assert_eq!(error.message, "Campo inválido");
        assert!(error.context.is_some());
        assert_eq!(error.status_code(), 400);
        assert!(error.is_operational());
    }

    #[test]
    fn test_app_error_to_response() {
        let error = AppError::not_found("Usuário não encontrado");
        let response = error.to_response();

        assert_eq!(response.error.kind, ErrorKind::NotFoundError);
        assert_eq!(response.error.message, "Usuário não encontrado");
        assert!(response.error.context.is_none());
    }
}

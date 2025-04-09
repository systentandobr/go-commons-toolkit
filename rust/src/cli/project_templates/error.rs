//! Módulo de gerenciamento de erros da aplicação

use actix_web::{HttpResponse, ResponseError};
use systentando_toolkit::error::{AppError as BaseAppError, ErrorKind, ErrorResponse};
use thiserror::Error;

pub use anyhow::{Result, Context};
pub use systentando_toolkit::error::ErrorKind;

/// Erro de aplicação
#[derive(Error, Debug)]
pub enum Error {
    /// Erro da toolkit
    #[error(transparent)]
    Toolkit(#[from] BaseAppError),
    
    /// Erro personalizado da aplicação
    #[error("{message}")]
    Custom {
        /// Tipo de erro
        kind: ErrorKind,
        /// Mensagem de erro
        message: String,
        /// Contexto adicional
        context: Option<serde_json::Value>,
    },
}

impl Error {
    /// Cria um novo erro personalizado
    pub fn custom<S: Into<String>>(kind: ErrorKind, message: S) -> Self {
        Self::Custom {
            kind,
            message: message.into(),
            context: None,
        }
    }
    
    /// Adiciona contexto ao erro
    pub fn with_context<T: serde::Serialize>(mut self, context: T) -> Self {
        if let Self::Custom { ref mut context: ctx, .. } = self {
            if let Ok(json) = serde_json::to_value(context) {
                *ctx = Some(json);
            }
        }
        self
    }
    
    /// Obtém o código HTTP associado ao erro
    pub fn status_code(&self) -> u16 {
        match self {
            Self::Toolkit(err) => err.status_code(),
            Self::Custom { kind, .. } => kind.status_code(),
        }
    }
    
    /// Converte para resposta HTTP
    pub fn to_response(&self) -> ErrorResponse {
        match self {
            Self::Toolkit(err) => err.to_response(),
            Self::Custom { kind, message, context } => ErrorResponse {
                error: systentando_toolkit::error::ErrorDetail {
                    kind: *kind,
                    message: message.clone(),
                    context: context.clone(),
                },
            },
        }
    }
}

/// Implementação de ResponseError para integração com Actix Web
impl ResponseError for Error {
    fn status_code(&self) -> actix_web::http::StatusCode {
        actix_web::http::StatusCode::from_u16(self.status_code())
            .unwrap_or(actix_web::http::StatusCode::INTERNAL_SERVER_ERROR)
    }
    
    fn error_response(&self) -> HttpResponse {
        let body = self.to_response();
        HttpResponse::build(self.status_code())
            .json(body)
    }
}

impl From<anyhow::Error> for Error {
    fn from(err: anyhow::Error) -> Self {
        if let Some(app_error) = err.downcast_ref::<BaseAppError>() {
            return Self::Toolkit(app_error.clone());
        }
        
        if let Some(custom_error) = err.downcast_ref::<Error>() {
            return custom_error.clone();
        }
        
        Self::custom(
            ErrorKind::InternalError,
            format!("Erro interno: {}", err)
        )
    }
}

impl Clone for Error {
    fn clone(&self) -> Self {
        match self {
            Self::Toolkit(err) => Self::Toolkit(err.clone()),
            Self::Custom { kind, message, context } => Self::Custom {
                kind: *kind,
                message: message.clone(),
                context: context.clone(),
            },
        }
    }
}

// Funções auxiliares para criar erros específicos

/// Cria um erro de validação
pub fn validation_error<S: Into<String>>(message: S) -> Error {
    Error::custom(ErrorKind::ValidationError, message)
}

/// Cria um erro de recurso não encontrado
pub fn not_found<S: Into<String>>(message: S) -> Error {
    Error::custom(ErrorKind::NotFoundError, message)
}

/// Cria um erro de autorização
pub fn unauthorized<S: Into<String>>(message: S) -> Error {
    Error::custom(ErrorKind::AuthorizationError, message)
}

/// Cria um erro de autenticação
pub fn unauthenticated<S: Into<String>>(message: S) -> Error {
    Error::custom(ErrorKind::AuthenticationError, message)
}

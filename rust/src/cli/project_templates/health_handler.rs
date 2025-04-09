//! Handler para verificação de saúde da aplicação

use actix_web::{HttpResponse, web};
use chrono::Utc;
use serde_json::json;
use tracing::info;

/// Verifica a saúde da aplicação
pub async fn health_check() -> HttpResponse {
    info!("Health check solicitado");
    
    let health_info = json!({
        "status": "ok",
        "timestamp": Utc::now().to_rfc3339(),
        "version": env!("CARGO_PKG_VERSION"),
        "service": env!("CARGO_PKG_NAME"),
    });
    
    HttpResponse::Ok().json(health_info)
}

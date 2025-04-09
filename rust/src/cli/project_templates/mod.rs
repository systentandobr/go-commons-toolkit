//! Templates para geração de projetos

// Importar todos os templates
pub mod config;
pub mod config_file;
pub mod dockerfile;
pub mod error;
pub mod health_handler;

/// Aplica valores ao template
pub fn apply_template(template: &str, replacements: &[(&str, &str)]) -> String {
    let mut result = template.to_string();
    for (key, value) in replacements {
        result = result.replace(&format!("{{{{{}}}}}", key), value);
    }
    result
}

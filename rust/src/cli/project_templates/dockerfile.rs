// Template para Dockerfile
pub const DOCKERFILE_TEMPLATE: &str = r#"# Builder stage
FROM rust:1.72-slim as builder

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y pkg-config libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy manifests
COPY Cargo.toml ./

# Create dummy source file to build dependencies
RUN mkdir -p src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

# Copy source code
COPY . .

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the compiled binary
COPY --from=builder /app/target/release/{{app_name}} /app/{{app_name}}

# Copy configuration directory
COPY --from=builder /app/config /app/config

# Set environment variables
ENV RUST_ENV=production

# Expose port
EXPOSE 8080

# Run the application
CMD ["/app/{{app_name}}"]
"#;

// Template para docker-compose.yml
pub const DOCKER_COMPOSE_TEMPLATE: &str = r#"version: '3.8'

services:
  app:
    build: .
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - RUST_ENV=production
      - APP__LOG_LEVEL=info
{{database_service}}
{{telemetry_service}}

volumes:
{{volumes}}
"#;

// Template para serviço de banco de dados PostgreSQL
pub const POSTGRES_SERVICE_TEMPLATE: &str = r#"
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={{app_name}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
"#;

// Template para serviço de telemetria
pub const TELEMETRY_SERVICE_TEMPLATE: &str = r#"
  jaeger:
    image: jaegertracing/all-in-one:latest
    restart: unless-stopped
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
"#;

// Template para volumes
pub const POSTGRES_VOLUME_TEMPLATE: &str = r#"
  postgres_data:
"#;

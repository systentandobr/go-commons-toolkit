# Ferramenta de Teste de Configuração e Conexão

Esta é uma ferramenta para validar as configurações e testar conexões com vários serviços usados pelo toolkit/go, como MongoDB, Supabase (PostgreSQL) e Kafka.

## Funcionalidades

- Verifica e exibe todas as configurações da aplicação
- Testa conexão com o MongoDB
  - Valida as configurações de URI e nome do banco
  - Conecta ao servidor e faz um ping
  - Acessa o banco de dados e uma coleção de teste
  - Executa uma operação simples (contagem de documentos)
- Testa conexão com o Supabase (PostgreSQL)
  - Valida as configurações de URI, banco, usuário e senha
  - Estabelece uma conexão com o servidor
  - Executa uma consulta SQL simples
- Testa configuração do Kafka
  - Valida as configurações como Bootstrap Server, Consumer Group, etc.
  - Cria um produtor Kafka para um tópico de teste
  - Cria um consumidor Kafka para um tópico de teste

## Como usar

1. Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

2. Edite o arquivo `.env` com as configurações corretas para seu ambiente:

```bash
nano .env
```

3. Execute o programa:

```bash
go run main.go
```

## Interpretando os resultados

- ✅ Indica configuração válida ou operação bem-sucedida
- ❌ Indica configuração padrão ou operação com falha

## Exemplos de saída

```
==== Teste de Configuração e Conexão ====
Validando configurações e testando conexões...
Arquivo .env carregado com sucesso.

=== Configurações da Aplicação ===
Ambiente: development
Porta API: 8080
Swagger: ✅ Configurado
CORS: ✅ Configurado
Jobs: ✅ Configurado
Métricas: ✅ Configurado
Tracing: ✅ Configurado

=== MongoDB ===
URI MongoDB             : ✅ mongodb://localhost:27017
Nome do Banco MongoDB   : ✅ my_app_db
Testando conexão: ✅ Conectado com sucesso
✅ Banco 'my_app_db' acessado com sucesso
✅ Coleção 'test_collection' acessada com sucesso
✅ Contagem de documentos: 0

=== Supabase/PostgreSQL ===
URI Supabase            : ✅ postgresql://db.example.com:5432
Nome do Banco           : ✅ my_database
Usuário                 : ✅ my_user
Senha                   : ✅ *****
Testando conexão: ✅ Conectado com sucesso
✅ Consulta executada com sucesso
  Versão PostgreSQL: PostgreSQL 14.5 on x86_64-pc-linux-gnu

=== Kafka ===
Bootstrap Server        : ✅ kafka.example.com:9092
Consumer Group ID       : ✅ my-app-consumer-group
Auto Offset Reset       : ✅ earliest
Auto Commit             : ✅ 
Tentando criar produtor: ✅ Produtor criado com sucesso para o tópico test-topic-producer
Tentando criar consumidor: ✅ Consumidor criado com sucesso para o tópico test-topic-consumer

==== Teste de Configuração Concluído ====
```

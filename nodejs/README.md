# Systentando Toolkit para Node.js

Este pacote fornece ferramentas, utilitários e padrões para desenvolvimento de microsserviços Node.js no ecossistema Systentando.

## Instalação

```bash
npm install @systentandobr/toolkit
```

## Funcionalidades

O toolkit inclui:

- **Telemetria/Observabilidade**: Implementação OpenTelemetry para rastreamento, métricas e logs
- **Validação**: Esquemas e utilidades para validação de dados
- **Gerenciamento de Configuração**: Carregamento e validação de configurações
- **Gerenciamento de Erros**: Classes de erro padronizadas e middleware para tratamento de erros
- **Segurança**: Utilitários para autenticação e autorização
- **Ferramentas de Desenvolvimento**: Templates e geradores para novos serviços
- **Clientes para Serviços Comuns**: API clients pré-configurados para serviços internos

## Uso

```typescript
import { createLogger, ConfigLoader, validate } from '@systentandobr/toolkit';

// Configuração de logger
const logger = createLogger('my-service');

// Carregamento de configurações
const config = ConfigLoader.load();

// Validação de dados
const validationSchema = { /* ... */ };
const validatedData = validate(data, validationSchema);
```

## Exemplos

Consulte a pasta `examples` para exemplos detalhados de uso.

## Contribuindo

Para contribuir com este toolkit, consulte nosso [Guia de Contribuição](../CONTRIBUTING.md).

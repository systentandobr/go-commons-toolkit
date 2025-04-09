import * as dotenv from 'dotenv';
import * as joi from 'joi';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Representa a configuração básica para qualquer microsserviço Systentando
 */
export interface BaseConfig {
  serviceName: string;
  environment: 'development' | 'staging' | 'production';
  port: number;
  logLevel: 'trace' | 'debug' | 'info' | 'warn' | 'error' | 'fatal';
  sentryDsn?: string;
  telemetry: {
    enabled: boolean;
    endpoint: string;
    serviceName: string;
  };
}

/**
 * Esquema de validação para a configuração básica
 */
const baseConfigSchema = joi.object({
  serviceName: joi.string().required(),
  environment: joi.string().valid('development', 'staging', 'production').required(),
  port: joi.number().port().required(),
  logLevel: joi.string().valid('trace', 'debug', 'info', 'warn', 'error', 'fatal').required(),
  sentryDsn: joi.string().uri().optional(),
  telemetry: joi.object({
    enabled: joi.boolean().required(),
    endpoint: joi.string().uri().when('enabled', { is: true, then: joi.required() }),
    serviceName: joi.string().when('enabled', { is: true, then: joi.required() }),
  }).required(),
});

/**
 * Classe para carregar e validar configurações de serviço
 */
export class ConfigLoader {
  /**
   * Carrega configurações a partir de arquivos .env e variáveis de ambiente
   * @param customSchema Esquema de validação adicional específico do serviço
   * @param configPath Caminho para o arquivo .env (opcional)
   * @returns Configuração validada
   */
  static load<T extends BaseConfig>(customSchema?: joi.ObjectSchema, configPath?: string): T {
    // Tenta carregar do .env se existir
    try {
      const envPath = configPath || process.env.NODE_ENV === 'test' 
        ? path.resolve(process.cwd(), '.env.test')
        : path.resolve(process.cwd(), '.env');

      if (fs.existsSync(envPath)) {
        dotenv.config({ path: envPath });
      }
    } catch (error) {
      console.warn('Não foi possível carregar o arquivo .env:', error);
    }

    // Construir configuração base a partir de variáveis de ambiente
    const baseConfig: BaseConfig = {
      serviceName: process.env.SERVICE_NAME || 'unknown-service',
      environment: (process.env.NODE_ENV as 'development' | 'staging' | 'production') || 'development',
      port: parseInt(process.env.PORT || '3000', 10),
      logLevel: (process.env.LOG_LEVEL as BaseConfig['logLevel']) || 'info',
      sentryDsn: process.env.SENTRY_DSN,
      telemetry: {
        enabled: process.env.TELEMETRY_ENABLED === 'true',
        endpoint: process.env.TELEMETRY_ENDPOINT || 'http://localhost:4318',
        serviceName: process.env.TELEMETRY_SERVICE_NAME || process.env.SERVICE_NAME || 'unknown-service',
      },
    };

    // Validar configuração base
    const { error: baseError, value: validatedBaseConfig } = baseConfigSchema.validate(baseConfig, {
      abortEarly: false,
    });

    if (baseError) {
      throw new Error(`Configuração base inválida: ${baseError.message}`);
    }

    // Se não houver schema personalizado, retorna a configuração base validada
    if (!customSchema) {
      return validatedBaseConfig as T;
    }

    // Validar com schema personalizado
    const finalSchema = baseConfigSchema.concat(customSchema);
    const { error, value } = finalSchema.validate(baseConfig, { abortEarly: false });

    if (error) {
      throw new Error(`Configuração inválida: ${error.message}`);
    }

    return value as T;
  }
}

export default ConfigLoader;

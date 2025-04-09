// Configuração
import ConfigLoader, { BaseConfig } from './config/config-loader';

// Utilitários
import createLogger, { Logger, LoggerService } from './utils/logger';
import { initTelemetry, shutdownTelemetry } from './utils/telemetry';
import metrics, { MetricsManager, MetricType } from './utils/metrics';
import * as errors from './utils/errors';
import validator from './utils/validator';
import httpClient from './utils/http-client';

// Ferramentas
import projectGenerator from './tools/project-generator';

/**
 * Inicializa o toolkit com configurações padrão
 * 
 * @param config Configuração opcional
 */
export function initialize(config?: Partial<BaseConfig>): void {
  // Carregar configuração completa se não fornecida
  const fullConfig = config 
    ? { ...ConfigLoader.load(), ...config }
    : ConfigLoader.load();
  
  // Configurar logger global
  LoggerService.configure(fullConfig.serviceName || 'toolkit', fullConfig);
  
  // Inicializar telemetria
  initTelemetry(fullConfig);
  
  // Registrar evento de inicialização
  metrics.incrementCounter('toolkit.initialized');
  
  // Configurar encerramento gracioso
  process.on('SIGTERM', async () => {
    await shutdown();
    process.exit(0);
  });
  
  process.on('SIGINT', async () => {
    await shutdown();
    process.exit(0);
  });
}

/**
 * Encerra o toolkit graciosamente
 */
export async function shutdown(): Promise<void> {
  const logger = LoggerService.getInstance();
  logger.info('Encerrando toolkit graciosamente...');
  
  try {
    // Registrar evento de encerramento
    metrics.incrementCounter('toolkit.shutdown');
    
    // Encerrar telemetria
    await shutdownTelemetry();
    
    logger.info('Toolkit encerrado com sucesso');
  } catch (error) {
    logger.error('Erro ao encerrar toolkit', { error });
  }
}

// Exportar todos os módulos
export {
  // Configuração
  ConfigLoader,
  BaseConfig,
  
  // Utilitários
  createLogger,
  Logger,
  LoggerService,
  metrics,
  MetricsManager,
  MetricType,
  errors,
  validator,
  httpClient,
  
  // Ferramentas
  projectGenerator,
};

// Exportação padrão
export default {
  initialize,
  shutdown,
  
  // Configuração
  ConfigLoader,
  
  // Utilitários
  createLogger,
  LoggerService,
  metrics,
  errors,
  validator,
  httpClient,
  
  // Ferramentas
  projectGenerator,
};

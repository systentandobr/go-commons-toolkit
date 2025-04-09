import * as winston from 'winston';
import { BaseConfig } from '../config/config-loader';

/**
 * Níveis de log disponíveis
 */
export type LogLevel = 'trace' | 'debug' | 'info' | 'warn' | 'error' | 'fatal';

/**
 * Interface do logger
 */
export interface Logger {
  trace(message: string, meta?: Record<string, unknown>): void;
  debug(message: string, meta?: Record<string, unknown>): void;
  info(message: string, meta?: Record<string, unknown>): void;
  warn(message: string, meta?: Record<string, unknown>): void;
  error(message: string, meta?: Record<string, unknown>): void;
  fatal(message: string, meta?: Record<string, unknown>): void;
}

/**
 * Cria um logger configurado para o ambiente Systentando
 * 
 * @param name Nome do módulo/componente
 * @param config Configuração opcional (caso já tenha uma instância de configuração)
 * @returns Uma instância de Logger
 */
export function createLogger(name: string, config?: Partial<BaseConfig>): Logger {
  const environment = config?.environment || process.env.NODE_ENV || 'development';
  const logLevel = config?.logLevel || (process.env.LOG_LEVEL as LogLevel) || 'info';
  const serviceName = config?.serviceName || process.env.SERVICE_NAME || 'unknown-service';
  
  // Converter níveis de log para formato Winston
  const levels = {
    trace: 0,
    debug: 1,
    info: 2,
    warn: 3,
    error: 4,
    fatal: 5,
  };

  // Definir cores para cada nível (no console)
  const colors = {
    trace: 'grey',
    debug: 'blue',
    info: 'green',
    warn: 'yellow',
    error: 'red',
    fatal: 'magenta',
  };

  // Adicionar cores ao winston
  winston.addColors(colors);

  // Formatar logs para desenvolvimento (mais legível para humanos)
  const developmentFormat = winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    winston.format.colorize({ all: true }),
    winston.format.printf(
      (info) => `${info.timestamp} ${info.level}: [${serviceName}:${name}] ${info.message} ${
        info.meta ? JSON.stringify(info.meta, null, 2) : ''
      }`
    )
  );

  // Formatar logs para produção (JSON estruturado)
  const productionFormat = winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  );

  // Criar a instância winston
  const winstonLogger = winston.createLogger({
    levels,
    level: logLevel,
    format: environment === 'development' ? developmentFormat : productionFormat,
    defaultMeta: { service: serviceName, module: name },
    transports: [
      new winston.transports.Console(),
    ],
  });

  // Retornar um wrapper que adiciona os métodos personalizados
  return {
    trace: (message: string, meta?: Record<string, unknown>) => 
      winstonLogger.log('trace', message, { meta }),
    debug: (message: string, meta?: Record<string, unknown>) => 
      winstonLogger.debug(message, { meta }),
    info: (message: string, meta?: Record<string, unknown>) => 
      winstonLogger.info(message, { meta }),
    warn: (message: string, meta?: Record<string, unknown>) => 
      winstonLogger.warn(message, { meta }),
    error: (message: string, meta?: Record<string, unknown>) => 
      winstonLogger.error(message, { meta }),
    fatal: (message: string, meta?: Record<string, unknown>) => 
      winstonLogger.log('fatal', message, { meta }),
  };
}

/**
 * Singleton para acessar o logger padrão da aplicação
 */
export class LoggerService {
  private static instance: Logger;

  /**
   * Obtém a instância do logger global
   */
  static getInstance(): Logger {
    if (!LoggerService.instance) {
      LoggerService.instance = createLogger('app');
    }
    return LoggerService.instance;
  }

  /**
   * Configura a instância do logger global
   */
  static configure(name: string, config?: Partial<BaseConfig>): void {
    LoggerService.instance = createLogger(name, config);
  }
}

export default createLogger;

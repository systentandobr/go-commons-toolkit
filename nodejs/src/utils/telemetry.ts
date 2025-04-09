import * as opentelemetry from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { LoggerService } from './logger';
import { BaseConfig } from '../config/config-loader';

/**
 * Indica se a telemetria está inicializada
 */
let isInitialized = false;

/**
 * Instância do SDK
 */
let sdk: opentelemetry.NodeSDK;

/**
 * Inicializa a telemetria para o serviço
 * @param config Configuração do serviço
 */
export function initTelemetry(config: BaseConfig): void {
  const logger = LoggerService.getInstance();

  if (isInitialized) {
    logger.warn('Telemetria já inicializada. Ignorando chamada.');
    return;
  }

  if (!config.telemetry.enabled) {
    logger.info('Telemetria desabilitada na configuração.');
    return;
  }

  try {
    // Configurar o exportador de traces para o endpoint configurado
    const traceExporter = new OTLPTraceExporter({
      url: `${config.telemetry.endpoint}/v1/traces`,
    });

    // Configurar o exportador de métricas
    const metricExporter = new OTLPMetricExporter({
      url: `${config.telemetry.endpoint}/v1/metrics`,
    });

    // Criar o recurso com os atributos semânticos
    const resource = new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: config.telemetry.serviceName,
      [SemanticResourceAttributes.SERVICE_VERSION]: process.env.npm_package_version || '0.0.0',
      [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: config.environment,
    });

    // Criar e inicializar o SDK
    sdk = new opentelemetry.NodeSDK({
      resource,
      traceExporter,
      metricReader: new opentelemetry.metrics.PeriodicExportingMetricReader({
        exporter: metricExporter,
        exportIntervalMillis: 60000, // Exportar a cada 60 segundos
      }),
      instrumentations: [
        getNodeAutoInstrumentations({
          // Configurações específicas para bibliotecas comuns
          '@opentelemetry/instrumentation-http': { enabled: true },
          '@opentelemetry/instrumentation-express': { enabled: true },
          '@opentelemetry/instrumentation-mongoose': { enabled: true },
          '@opentelemetry/instrumentation-ioredis': { enabled: true },
          '@opentelemetry/instrumentation-pg': { enabled: true },
          '@opentelemetry/instrumentation-mongodb': { enabled: true },
        }),
      ],
    });

    // Inicializar o SDK
    sdk.start();
    isInitialized = true;
    logger.info('Telemetria inicializada com sucesso', {
      endpoint: config.telemetry.endpoint,
      serviceName: config.telemetry.serviceName,
    });
  } catch (error) {
    logger.error('Erro ao inicializar telemetria', { error });
  }
}

/**
 * Finaliza a telemetria de forma graciosa
 * @returns Promise que resolve quando o shutdown é concluído
 */
export async function shutdownTelemetry(): Promise<void> {
  const logger = LoggerService.getInstance();
  if (!isInitialized || !sdk) {
    logger.debug('Telemetria não está inicializada. Nada para finalizar.');
    return;
  }

  try {
    await sdk.shutdown();
    isInitialized = false;
    logger.info('Telemetria finalizada com sucesso');
  } catch (error) {
    logger.error('Erro ao finalizar telemetria', { error });
  }
}

export default {
  initTelemetry,
  shutdownTelemetry,
};

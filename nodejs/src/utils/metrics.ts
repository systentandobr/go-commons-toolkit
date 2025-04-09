import * as os from 'os';
import { LoggerService } from './logger';

// Referenciamos a API de OpenTelemetry para métricas exportadas pelo telemetry.ts
import * as api from '@opentelemetry/api';

const logger = LoggerService.getInstance();

/**
 * Tipos de métricas suportadas
 */
export enum MetricType {
  COUNTER = 'counter',
  GAUGE = 'gauge',
  HISTOGRAM = 'histogram',
}

/**
 * Classe para gerenciamento de métricas da aplicação
 */
export class MetricsManager {
  private static instance: MetricsManager;
  private meter: api.Meter;
  private metrics: Map<string, any> = new Map();
  private isEnabled: boolean = false;
  private metricsPrefix: string;
  private defaultLabels: Record<string, string>;
  
  /**
   * Construtor privado para o padrão Singleton
   */
  private constructor() {
    this.metricsPrefix = process.env.METRICS_PREFIX || 'app';
    const serviceName = process.env.SERVICE_NAME || 'unknown-service';
    
    this.defaultLabels = {
      service: serviceName,
      host: os.hostname(),
      environment: process.env.NODE_ENV || 'development',
    };
    
    try {
      // Tentar obter o meter da API OpenTelemetry
      this.meter = api.metrics.getMeter(serviceName);
      this.isEnabled = true;
    } catch (error) {
      logger.warn('OpenTelemetry não está configurado. As métricas serão registradas apenas em logs.', {
        error: error instanceof Error ? error.message : String(error),
      });
      this.isEnabled = false;
      // Inicializar meter como um objeto vazio
      this.meter = {} as api.Meter;
    }
    
    // Registrar métricas padrão do sistema
    this.registerSystemMetrics();
  }
  
  /**
   * Obtém a instância singleton do gerenciador de métricas
   */
  static getInstance(): MetricsManager {
    if (!MetricsManager.instance) {
      MetricsManager.instance = new MetricsManager();
    }
    return MetricsManager.instance;
  }
  
  /**
   * Registra métricas padrão do sistema (CPU, memória, etc)
   */
  private registerSystemMetrics(): void {
    if (!this.isEnabled) return;
    
    try {
      // Métrica de uso de CPU
      const cpuUsageGauge = this.meter.createObservableGauge(`${this.metricsPrefix}.system.cpu_usage`, {
        description: 'Percentual de uso de CPU',
        unit: '%',
      });
      
      cpuUsageGauge.addCallback((observableResult: api.ObservableResult) => {
        const cpuUsage = this.getCpuUsage();
        observableResult.observe(cpuUsage, this.defaultLabels);
      });
      
      // Métrica de uso de memória
      const memoryUsageGauge = this.meter.createObservableGauge(`${this.metricsPrefix}.system.memory_usage`, {
        description: 'Uso de memória em bytes',
        unit: 'bytes',
      });
      
      memoryUsageGauge.addCallback((observableResult: api.ObservableResult) => {
        const memoryUsage = process.memoryUsage();
        observableResult.observe(memoryUsage.rss, { ...this.defaultLabels, type: 'rss' });
        observableResult.observe(memoryUsage.heapTotal, { ...this.defaultLabels, type: 'heapTotal' });
        observableResult.observe(memoryUsage.heapUsed, { ...this.defaultLabels, type: 'heapUsed' });
        observableResult.observe(memoryUsage.external, { ...this.defaultLabels, type: 'external' });
      });
      
      // Métrica de carga do sistema
      const loadAverageGauge = this.meter.createObservableGauge(`${this.metricsPrefix}.system.load_average`, {
        description: 'Média de carga do sistema',
        unit: '',
      });
      
      loadAverageGauge.addCallback((observableResult: api.ObservableResult) => {
        const loadAverage = os.loadavg();
        observableResult.observe(loadAverage[0], { ...this.defaultLabels, interval: '1m' });
        observableResult.observe(loadAverage[1], { ...this.defaultLabels, interval: '5m' });
        observableResult.observe(loadAverage[2], { ...this.defaultLabels, interval: '15m' });
      });
    } catch (error) {
      logger.warn('Erro ao registrar métricas do sistema:', { error });
    }
  }
  
  /**
   * Calcula o uso de CPU como porcentagem
   */
  private getCpuUsage(): number {
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;
    
    for (const cpu of cpus) {
      for (const type in cpu.times) {
        totalTick += cpu.times[type as keyof typeof cpu.times];
      }
      totalIdle += cpu.times.idle;
    }
    
    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;
    return 100 - (idle / total) * 100;
  }
  
  /**
   * Incrementa um contador
   * 
   * @param name Nome da métrica
   * @param value Valor a incrementar (padrão: 1)
   * @param labels Labels adicionais
   */
  incrementCounter(
    name: string,
    value: number = 1,
    labels: Record<string, string> = {}
  ): void {
    const metricName = `${this.metricsPrefix}.${name}`;
    
    // Se telemetria estiver habilitada, usar OpenTelemetry
    if (this.isEnabled) {
      try {
        let counter = this.metrics.get(metricName);
        
        if (!counter) {
          counter = this.meter.createCounter(metricName, {
            description: `Counter para ${name}`,
          });
          this.metrics.set(metricName, counter);
        }
        
        const allLabels = { ...this.defaultLabels, ...labels };
        counter.add(value, allLabels);
      } catch (error) {
        logger.warn(`Erro ao incrementar contador ${metricName}:`, { error });
      }
    }
    
    // Registrar também no log para debug
    logger.debug(`Métrica incrementada: ${metricName}`, {
      type: MetricType.COUNTER,
      name: metricName,
      value,
      labels: { ...this.defaultLabels, ...labels },
    });
  }
  
  /**
   * Registra um valor em uma métrica de gauge
   * 
   * @param name Nome da métrica
   * @param value Valor atual
   * @param labels Labels adicionais
   */
  setGauge(
    name: string,
    value: number,
    labels: Record<string, string> = {}
  ): void {
    const metricName = `${this.metricsPrefix}.${name}`;
    
    // Se telemetria estiver habilitada, usar OpenTelemetry
    if (this.isEnabled) {
      try {
        // Armazenar o valor e labels para uso posterior
        this.metrics.set(`${metricName}_value`, value);
        this.metrics.set(`${metricName}_labels`, { ...this.defaultLabels, ...labels });
        
        // Verificar se o gauge já existe
        if (!this.metrics.has(metricName)) {
          const gauge = this.meter.createObservableGauge(metricName, {
            description: `Gauge para ${name}`,
          });
          
          gauge.addCallback((observableResult: api.ObservableResult) => {
            const lastValue = this.metrics.get(`${metricName}_value`) || 0;
            const lastLabels = this.metrics.get(`${metricName}_labels`) || this.defaultLabels;
            observableResult.observe(lastValue, lastLabels);
          });
          
          this.metrics.set(metricName, gauge);
        }
      } catch (error) {
        logger.warn(`Erro ao atualizar gauge ${metricName}:`, { error });
      }
    }
    
    // Registrar também no log para debug
    logger.debug(`Métrica gauge atualizada: ${metricName}`, {
      type: MetricType.GAUGE,
      name: metricName,
      value,
      labels: { ...this.defaultLabels, ...labels },
    });
  }
  
  /**
   * Registra um valor em um histograma
   * 
   * @param name Nome da métrica
   * @param value Valor a ser registrado
   * @param labels Labels adicionais
   */
  recordHistogram(
    name: string,
    value: number,
    labels: Record<string, string> = {}
  ): void {
    const metricName = `${this.metricsPrefix}.${name}`;
    
    // Se telemetria estiver habilitada, usar OpenTelemetry
    if (this.isEnabled) {
      try {
        let histogram = this.metrics.get(metricName);
        
        if (!histogram) {
          histogram = this.meter.createHistogram(metricName, {
            description: `Histograma para ${name}`,
          });
          this.metrics.set(metricName, histogram);
        }
        
        const allLabels = { ...this.defaultLabels, ...labels };
        histogram.record(value, allLabels);
      } catch (error) {
        logger.warn(`Erro ao registrar histograma ${metricName}:`, { error });
      }
    }
    
    // Registrar também no log para debug
    logger.debug(`Métrica histograma registrada: ${metricName}`, {
      type: MetricType.HISTOGRAM,
      name: metricName,
      value,
      labels: { ...this.defaultLabels, ...labels },
    });
  }
  
  /**
   * Mede o tempo de execução de uma função
   * 
   * @param name Nome da métrica
   * @param fn Função a ser medida
   * @param labels Labels adicionais
   * @returns Resultado da função
   */
  async measureTime<T>(
    name: string,
    fn: () => Promise<T> | T,
    labels: Record<string, string> = {}
  ): Promise<T> {
    const start = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - start;
      this.recordHistogram(`${name}_duration_ms`, duration, labels);
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      this.recordHistogram(`${name}_duration_ms`, duration, {
        ...labels,
        success: 'false',
        error: error instanceof Error ? error.name : 'unknown',
      });
      throw error;
    }
  }
}

/**
 * Exporta uma instância singleton do gerenciador de métricas
 */
export const metrics = MetricsManager.getInstance();

export default metrics;

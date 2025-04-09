import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { LoggerService } from './logger';
import { ExternalServiceError } from './errors';

/**
 * Opções para o cliente HTTP
 */
export interface HttpClientOptions {
  /**
   * URL base para todas as requisições
   */
  baseUrl: string;
  
  /**
   * Timeout em milissegundos
   */
  timeout?: number;
  
  /**
   * Headers padrão para todas as requisições
   */
  headers?: Record<string, string>;
  
  /**
   * Nome do serviço (para logs)
   */
  serviceName?: string;
  
  /**
   * Número máximo de tentativas
   */
  maxRetries?: number;
  
  /**
   * Tempo base para retry exponencial (ms)
   */
  retryDelay?: number;
}

// Estender a interface InternalAxiosRequestConfig para incluir retryCount
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    retryCount?: number;
  }
}

/**
 * Cliente HTTP com suporte a retry, logging e tratamento de erros
 */
export class HttpClient {
  private client: AxiosInstance;
  private logger = LoggerService.getInstance();
  private options: HttpClientOptions;
  
  constructor(options: HttpClientOptions) {
    this.options = {
      timeout: 10000,
      maxRetries: 3,
      retryDelay: 300,
      ...options
    };
    
    this.client = axios.create({
      baseURL: this.options.baseUrl,
      timeout: this.options.timeout,
      headers: this.options.headers,
    });
    
    // Adicionar interceptors para logging
    this.setupInterceptors();
  }
  
  /**
   * Configura interceptors para logging e retry
   */
  private setupInterceptors(): void {
    // Interceptor de requisição para logging
    this.client.interceptors.request.use(
      (config) => {
        const { method, url, data } = config;
        this.logger.debug(`HTTP ${method?.toUpperCase()} request`, {
          service: this.options.serviceName,
          url: `${this.options.baseUrl}${url}`,
          method,
          data: this.sanitizeData(data)
        });
        
        // Adicionar contador de tentativas ao config
        config.retryCount = config.retryCount || 0;
        
        return config;
      },
      (error) => {
        this.logger.error(`HTTP request error`, {
          service: this.options.serviceName,
          error: error.message
        });
        return Promise.reject(error);
      }
    );
    
    // Interceptor de resposta para logging e retry
    this.client.interceptors.response.use(
      (response) => {
        const { status, config } = response;
        const { method, url } = config;
        
        this.logger.debug(`HTTP ${method?.toUpperCase()} response: ${status}`, {
          service: this.options.serviceName,
          url: `${this.options.baseUrl}${url}`,
          method,
          status,
        });
        
        return response;
      },
      async (error) => {
        const config = error.config;
        
        // Se não tiver config, não é um erro de requisição
        if (!config) {
          return Promise.reject(error);
        }
        
        // Log do erro
        this.logger.error(`HTTP response error`, {
          service: this.options.serviceName,
          url: `${this.options.baseUrl}${config.url}`,
          method: config.method?.toUpperCase(),
          status: error.response?.status,
          error: error.message,
          retryCount: config.retryCount
        });
        
        // Verificar se deve fazer retry
        if (
          config.retryCount < (this.options.maxRetries || 3) && 
          this.shouldRetry(error)
        ) {
          config.retryCount += 1;
          
          // Delay exponencial
          const delay = 
            (this.options.retryDelay || 300) * Math.pow(2, config.retryCount - 1) +
            Math.random() * 100;
          
          await new Promise(resolve => setTimeout(resolve, delay));
          
          this.logger.debug(`Retrying request (${config.retryCount}/${this.options.maxRetries})`, {
            service: this.options.serviceName,
            url: `${this.options.baseUrl}${config.url}`,
            method: config.method?.toUpperCase()
          });
          
          return this.client(config);
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Decide se uma requisição deve ser repetida com base no erro
   */
  private shouldRetry(error: any): boolean {
    // Não repetir em caso de erro 4xx (exceto 408 - timeout e 429 - rate limit)
    if (
      error.response && 
      error.response.status >= 400 && 
      error.response.status < 500 &&
      error.response.status !== 408 &&
      error.response.status !== 429
    ) {
      return false;
    }
    
    // Repetir em caso de erro de rede, timeout ou 5xx
    return true;
  }
  
  /**
   * Sanitiza dados sensíveis para logs
   */
  private sanitizeData(data: any): any {
    if (!data) return data;
    
    // Clone para não modificar o original
    const sanitized = JSON.parse(JSON.stringify(data));
    
    // Lista de chaves sensíveis
    const sensitiveKeys = [
      'password', 'senha', 'token', 'secret', 'key', 'apiKey', 
      'api_key', 'accessToken', 'access_token', 'authorization'
    ];
    
    // Função recursiva para sanitizar
    const sanitizeObject = (obj: any): any => {
      if (!obj || typeof obj !== 'object') return obj;
      
      // Para arrays, sanitizar cada item
      if (Array.isArray(obj)) {
        return obj.map(sanitizeObject);
      }
      
      // Para objetos, sanitizar chaves sensíveis
      Object.keys(obj).forEach(key => {
        if (typeof obj[key] === 'object' && obj[key] !== null) {
          obj[key] = sanitizeObject(obj[key]);
        } else if (sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
          obj[key] = '***REDACTED***';
        }
      });
      
      return obj;
    };
    
    return sanitizeObject(sanitized);
  }
  
  /**
   * Faz uma requisição GET
   */
  async get<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.get<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error; // Nunca deve chegar aqui por causa do handleError
    }
  }
  
  /**
   * Faz uma requisição POST
   */
  async post<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error; // Nunca deve chegar aqui por causa do handleError
    }
  }
  
  /**
   * Faz uma requisição PUT
   */
  async put<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error; // Nunca deve chegar aqui por causa do handleError
    }
  }
  
  /**
   * Faz uma requisição PATCH
   */
  async patch<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error; // Nunca deve chegar aqui por causa do handleError
    }
  }
  
  /**
   * Faz uma requisição DELETE
   */
  async delete<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.delete<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error; // Nunca deve chegar aqui por causa do handleError
    }
  }
  
  /**
   * Manipula erros de requisição
   */
  private handleError(error: any): never {
    const serviceName = this.options.serviceName || 'external-service';
    const status = error.response?.status;
    const data = error.response?.data;
    
    // Criar mensagem de erro detalhada
    let message = `Erro ao conectar com ${serviceName}`;
    if (status) {
      message += `: status ${status}`;
    }
    
    throw new ExternalServiceError(message, {
      service: serviceName,
      status,
      data,
      originalError: error.message
    });
  }
}

/**
 * Cria um novo cliente HTTP
 */
export function createHttpClient(options: HttpClientOptions): HttpClient {
  return new HttpClient(options);
}

export default {
  HttpClient,
  createHttpClient
};

/**
 * Classe base para erros da aplicação
 */
export class AppError extends Error {
  public readonly name: string;
  public readonly httpCode: number;
  public readonly isOperational: boolean;
  public readonly context?: Record<string, unknown>;

  constructor(
    name: string,
    httpCode: number,
    description: string,
    isOperational: boolean,
    context?: Record<string, unknown>
  ) {
    super(description);

    Object.setPrototypeOf(this, new.target.prototype); // restaurar cadeia de prototype
    
    this.name = name;
    this.httpCode = httpCode;
    this.isOperational = isOperational;
    this.context = context;
    
    Error.captureStackTrace(this);
  }
}

/**
 * Erro para solicitações com dados inválidos
 */
export class ValidationError extends AppError {
  constructor(description: string, context?: Record<string, unknown>) {
    super('VALIDATION_ERROR', 400, description, true, context);
  }
}

/**
 * Erro para recursos não encontrados
 */
export class NotFoundError extends AppError {
  constructor(description: string = 'Recurso não encontrado', context?: Record<string, unknown>) {
    super('NOT_FOUND_ERROR', 404, description, true, context);
  }
}

/**
 * Erro para falhas internas do sistema
 */
export class InternalError extends AppError {
  constructor(description: string = 'Erro interno do servidor', context?: Record<string, unknown>) {
    super('INTERNAL_ERROR', 500, description, false, context);
  }
}

/**
 * Erro para falhas em serviços externos
 */
export class ExternalServiceError extends AppError {
  constructor(description: string = 'Erro em serviço externo', context?: Record<string, unknown>) {
    super('EXTERNAL_SERVICE_ERROR', 502, description, true, context);
  }
}

export default {
  AppError,
  ValidationError,
  NotFoundError,
  InternalError,
  ExternalServiceError
};

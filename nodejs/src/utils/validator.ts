import * as joi from 'joi';
import { ValidationError } from './errors';

/**
 * Valida dados de acordo com um esquema Joi
 * 
 * @param data Dados a serem validados
 * @param schema Esquema Joi para validação
 * @param options Opções de validação
 * @returns Dados validados (e convertidos, se aplicável)
 * @throws ValidationError se os dados forem inválidos
 */
export function validate<T>(
  data: unknown,
  schema: joi.Schema,
  options: joi.ValidationOptions = { abortEarly: false }
): T {
  const { error, value } = schema.validate(data, options);
  
  if (error) {
    const details = error.details.map(detail => ({
      message: detail.message,
      path: detail.path,
      type: detail.type
    }));
    
    throw new ValidationError(
      'Dados de entrada inválidos', 
      { details }
    );
  }
  
  return value as T;
}

/**
 * Cria um middleware de validação para Express
 * 
 * @param schema Esquema Joi para validação
 * @param source Fonte dos dados a serem validados (body, query, params)
 * @returns Middleware Express para validação
 */
export function createValidationMiddleware(
  schema: joi.Schema,
  source: 'body' | 'query' | 'params' = 'body'
) {
  return (req: any, res: any, next: any) => {
    try {
      const data = req[source];
      const validatedData = validate(data, schema);
      req[source] = validatedData;
      next();
    } catch (error) {
      if (error instanceof ValidationError) {
        return res.status(400).json({
          error: {
            name: error.name,
            message: error.message,
            context: error.context
          }
        });
      }
      next(error);
    }
  };
}

/**
 * Esquemas comuns para reutilização
 */
export const commonSchemas = {
  /**
   * Schema para UUID v4
   */
  uuid: joi.string().guid({ version: 'uuidv4' }),
  
  /**
   * Schema para email
   */
  email: joi.string().email(),
  
  /**
   * Schema para senha forte
   */
  password: joi.string().min(8).pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\W]{8,}$/),
  
  /**
   * Schema para nome de usuário
   */
  username: joi.string().alphanum().min(3).max(30),
  
  /**
   * Schema para número de telefone
   */
  phone: joi.string().pattern(/^\+?[0-9]{10,15}$/),
  
  /**
   * Schema para URL
   */
  url: joi.string().uri(),
  
  /**
   * Schema para data ISO
   */
  isoDate: joi.string().isoDate(),
  
  /**
   * Schema para paginação
   */
  pagination: joi.object({
    page: joi.number().integer().min(1).default(1),
    limit: joi.number().integer().min(1).max(100).default(20)
  }),
  
  /**
   * Schema para ordenação
   */
  sorting: joi.object({
    sortBy: joi.string(),
    order: joi.string().valid('asc', 'desc').default('asc')
  })
};

export default {
  validate,
  createValidationMiddleware,
  commonSchemas,
};

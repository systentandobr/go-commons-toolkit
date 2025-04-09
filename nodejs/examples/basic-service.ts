import express from 'express';
import * as toolkit from '../src/index';

// Inicializar o toolkit
toolkit.initialize({
  serviceName: 'example-service',
  environment: 'development',
  logLevel: 'debug',
  telemetry: {
    enabled: true,
    endpoint: 'http://localhost:4318',
    serviceName: 'example-service',
  },
});

// Obter logger
const logger = toolkit.createLogger('app');

// Criar servidor Express
const app = express();
const port = process.env.PORT || 3000;

// Middleware para métricas de requisição
app.use((req, res, next) => {
  const start = Date.now();
  
  // Capturar quando a resposta for enviada
  res.on('finish', () => {
    const duration = Date.now() - start;
    const statusCode = res.statusCode;
    const method = req.method;
    const path = req.path;
    
    // Registrar métricas
    toolkit.metrics.incrementCounter('http.requests', 1, {
      method,
      path,
      status: statusCode.toString(),
    });
    
    toolkit.metrics.recordHistogram('http.request_duration_ms', duration, {
      method,
      path,
      status: statusCode.toString(),
    });
    
    // Log de requisição
    logger.info(`${method} ${path} ${statusCode} - ${duration}ms`);
  });
  
  next();
});

// Endpoint de exemplo que demonstra validação
app.post('/users', express.json(), (req, res) => {
  try {
    // Esquema de validação usando Joi
    const userSchema = toolkit.validator.commonSchemas.username;
    const emailSchema = toolkit.validator.commonSchemas.email;
    
    // Validar dados
    const schema = {
      username: userSchema.required(),
      email: emailSchema.required(),
      age: toolkit.validator.commonSchemas.password.optional(),
    };
    
    // Validar corpo da requisição
    toolkit.validator.validate(req.body, toolkit.validator.joi.object(schema));
    
    // Responder com sucesso
    return res.status(201).json({
      message: 'Usuário criado com sucesso',
      user: req.body,
    });
  } catch (error) {
    // Tratar erro de validação
    if (error instanceof toolkit.errors.ValidationError) {
      return res.status(400).json({
        error: {
          name: error.name,
          message: error.message,
          context: error.context,
        },
      });
    }
    
    // Outro tipo de erro
    logger.error('Erro ao processar requisição', { error });
    return res.status(500).json({
      error: {
        name: 'INTERNAL_ERROR',
        message: 'Erro interno do servidor',
      },
    });
  }
});

// Endpoint de saúde
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    version: process.env.npm_package_version || '0.0.0',
    uptime: process.uptime(),
  });
});

// Iniciar servidor
app.listen(port, () => {
  logger.info(`Servidor iniciado na porta ${port}`);
  
  // Registrar evento de inicialização
  toolkit.metrics.incrementCounter('app.started');
  
  // Registrar algumas métricas de exemplo
  toolkit.metrics.setGauge('app.connections', 0);
  
  // Simular algumas métricas para exemplo
  setInterval(() => {
    const connections = Math.floor(Math.random() * 100);
    toolkit.metrics.setGauge('app.connections', connections);
    
    const responseTime = Math.random() * 500;
    toolkit.metrics.recordHistogram('app.simulated_response_time', responseTime);
  }, 5000);
});

// Manipular encerramento gracioso
process.on('SIGTERM', async () => {
  logger.info('Recebido sinal SIGTERM, encerrando graciosamente...');
  
  // Encerrar o toolkit
  await toolkit.shutdown();
  
  process.exit(0);
});

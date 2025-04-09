import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { createLogger } from '../utils/logger';

const logger = createLogger('project-generator');
const writeFileAsync = promisify(fs.writeFile);
const mkdirAsync = promisify(fs.mkdir);

/**
 * Opções para geração de um novo microsserviço
 */
export interface MicroserviceOptions {
  name: string;
  description?: string;
  author?: string;
  includeExpress?: boolean;
  includeMongoDB?: boolean;
  includeORM?: boolean;
  includeTests?: boolean;
  includeDocker?: boolean;
  outputDir: string;
}

/**
 * Gera a estrutura de um novo projeto de microsserviço
 */
export async function generateMicroservice(options: MicroserviceOptions): Promise<void> {
  const {
    name,
    description = `${name} microservice`,
    author = 'SystentandoBR',
    includeExpress = true,
    includeMongoDB = false,
    includeORM = false,
    includeTests = true,
    includeDocker = true,
    outputDir,
  } = options;

  logger.info(`Gerando microsserviço: ${name}`, { options });

  const projectDir = path.join(outputDir, name);

  try {
    // Criar diretório do projeto se não existir
    await mkdirAsync(projectDir, { recursive: true });

    // Criar estrutura de diretórios
    const directories = [
      'src',
      'src/config',
      'src/controllers',
      'src/models',
      'src/routes',
      'src/services',
      'src/utils',
      includeTests ? 'test' : null,
      includeDocker ? 'docker' : null,
    ].filter(Boolean);

    for (const dir of directories) {
      await mkdirAsync(path.join(projectDir, dir as string), { recursive: true });
    }

    // Gerar package.json
    const dependencies: Record<string, string> = {
      '@systentandobr/toolkit': '^0.1.0',
      'dotenv': '^16.3.1',
    };

    if (includeExpress) {
      dependencies['express'] = '^4.18.2';
      dependencies['cors'] = '^2.8.5';
      dependencies['helmet'] = '^7.0.0';
    }

    if (includeMongoDB) {
      dependencies['mongoose'] = '^7.4.1';
    }

    if (includeORM) {
      dependencies['typeorm'] = '^0.3.17';
      dependencies['pg'] = '^8.11.2';
    }

    const devDependencies: Record<string, string> = {
      '@types/node': '^20.4.5',
      'typescript': '^5.1.6',
      'ts-node': '^10.9.1',
      'nodemon': '^3.0.1',
    };

    if (includeExpress) {
      devDependencies['@types/express'] = '^4.17.17';
      devDependencies['@types/cors'] = '^2.8.13';
    }

    if (includeTests) {
      devDependencies['jest'] = '^29.6.2';
      devDependencies['@types/jest'] = '^29.5.3';
      devDependencies['ts-jest'] = '^29.1.1';
      devDependencies['supertest'] = '^6.3.3';
      devDependencies['@types/supertest'] = '^2.0.12';
    }

    const packageJson = {
      name: `@systentandobr/${name}`,
      version: '0.1.0',
      description,
      main: 'dist/index.js',
      scripts: {
        'build': 'tsc',
        'start': 'node dist/index.js',
        'dev': 'nodemon src/index.ts',
        'lint': 'eslint \\"src/**/*.ts\\"',
        ...(includeTests ? { 'test': 'jest' } : {}),
      },
      author,
      license: 'MIT',
      dependencies,
      devDependencies,
    };

    await writeFileAsync(
      path.join(projectDir, 'package.json'),
      JSON.stringify(packageJson, null, 2)
    );

    // Gerar tsconfig.json
    const tsConfig = {
      compilerOptions: {
        target: 'ES2022',
        module: 'CommonJS',
        outDir: './dist',
        rootDir: './src',
        strict: true,
        esModuleInterop: true,
        skipLibCheck: true,
        forceConsistentCasingInFileNames: true,
        resolveJsonModule: true,
      },
      include: ['src/**/*'],
      exclude: ['node_modules', '**/*.test.ts', 'dist'],
    };

    await writeFileAsync(
      path.join(projectDir, 'tsconfig.json'),
      JSON.stringify(tsConfig, null, 2)
    );

    // Gerar .env.example
    const envExample = [
      '# Configuração do serviço',
      `SERVICE_NAME=${name}`,
      'PORT=3000',
      'NODE_ENV=development',
      'LOG_LEVEL=debug',
      '',
      '# Telemetria',
      'TELEMETRY_ENABLED=true',
      'TELEMETRY_ENDPOINT=http://localhost:4318',
      `TELEMETRY_SERVICE_NAME=${name}`,
      '',
      includeMongoDB ? '# MongoDB\nMONGODB_URI=mongodb://localhost:27017/' + name : '',
      includeORM ? '# Database\nDB_HOST=localhost\nDB_PORT=5432\nDB_USER=postgres\nDB_PASS=postgres\nDB_NAME=' + name : '',
    ].filter(Boolean).join('\n');

    await writeFileAsync(path.join(projectDir, '.env.example'), envExample);

    // Gerar .gitignore
    const gitignore = [
      '# dependencies',
      '/node_modules',
      '/.pnp',
      '.pnp.js',
      '',
      '# testing',
      '/coverage',
      '',
      '# production',
      '/dist',
      '/build',
      '',
      '# misc',
      '.DS_Store',
      '.env',
      '.env.local',
      '.env.development.local',
      '.env.test.local',
      '.env.production.local',
      '',
      'npm-debug.log*',
      'yarn-debug.log*',
      'yarn-error.log*',
      '',
      '# IDE',
      '.idea/',
      '.vscode/',
      '*.sublime-*',
      '',
      '# Logs',
      'logs',
      '*.log',
    ].join('\n');

    await writeFileAsync(path.join(projectDir, '.gitignore'), gitignore);

    // Gerar index.ts básico
    const indexTemplate = [
      "import { ConfigLoader } from '@systentandobr/toolkit/dist/config/config-loader';",
      "import { LoggerService } from '@systentandobr/toolkit/dist/utils/logger';",
      "import { initTelemetry } from '@systentandobr/toolkit/dist/utils/telemetry';",
      includeExpress ? "import express from 'express';" : '',
      includeExpress ? "import cors from 'cors';" : '',
      includeExpress ? "import helmet from 'helmet';" : '',
      '',
      '// Carregar configuração',
      'const config = ConfigLoader.load();',
      '',
      '// Configurar logger',
      'LoggerService.configure(config.serviceName, config);',
      'const logger = LoggerService.getInstance();',
      '',
      '// Inicializar telemetria',
      'initTelemetry(config);',
      '',
      includeExpress ? '// Configurar Express\nconst app = express();\n\n// Middleware\napp.use(helmet());\napp.use(cors());\napp.use(express.json());\n' : '',
      includeExpress ? '// Rotas\napp.get("/health", (req, res) => {\n  res.json({ status: "ok", service: config.serviceName });\n});\n' : '',
      includeExpress ? '// Iniciar servidor\napp.listen(config.port, () => {\n  logger.info(`Servidor rodando na porta ${config.port}`);\n});' : 'logger.info(`Serviço ${config.serviceName} iniciado`);',
      '',
      '// Capturar encerramento do processo',
      'process.on("SIGTERM", () => {',
      '  logger.info("Recebido sinal SIGTERM, encerrando graciosamente...");',
      '  // TODO: Código de limpeza (fechar conexões, etc.)',
      '  process.exit(0);',
      '});',
    ].filter(Boolean).join('\n');

    await writeFileAsync(path.join(projectDir, 'src', 'index.ts'), indexTemplate);

    // Gerar README.md
    const readme = [
      `# ${name}`,
      '',
      description,
      '',
      '## Instalação',
      '',
      '```bash',
      'npm install',
      '```',
      '',
      '## Configuração',
      '',
      '1. Copie o arquivo `.env.example` para `.env`',
      '2. Ajuste as variáveis de ambiente conforme necessário',
      '',
      '## Desenvolvimento',
      '',
      '```bash',
      'npm run dev',
      '```',
      '',
      '## Produção',
      '',
      '```bash',
      'npm run build',
      'npm start',
      '```',
      '',
      includeTests ? '## Testes\n\n```bash\nnpm test\n```\n' : '',
      includeDocker ? '## Docker\n\n```bash\ndocker-compose up -d\n```\n' : '',
    ].filter(Boolean).join('\n');

    await writeFileAsync(path.join(projectDir, 'README.md'), readme);

    // Gerar Dockerfile se necessário
    if (includeDocker) {
      const dockerfile = [
        'FROM node:18-alpine',
        '',
        'WORKDIR /app',
        '',
        'COPY package*.json ./',
        '',
        'RUN npm ci --only=production',
        '',
        'COPY ./dist ./dist',
        '',
        'EXPOSE 3000',
        '',
        'CMD ["node", "dist/index.js"]',
      ].join('\n');

      await writeFileAsync(path.join(projectDir, 'Dockerfile'), dockerfile);

      // Gerar docker-compose.yml
      const dockerCompose = [
        'version: "3.8"',
        '',
        'services:',
        `  ${name}:`,
        '    build: .',
        '    restart: unless-stopped',
        '    ports:',
        '      - "3000:3000"',
        '    environment:',
        '      - NODE_ENV=production',
        '      - PORT=3000',
        includeMongoDB ? `  mongodb:\n    image: mongo:6\n    restart: unless-stopped\n    ports:\n      - "27017:27017"\n    volumes:\n      - mongo-data:/data/db` : '',
        includeORM ? `  postgres:\n    image: postgres:15\n    restart: unless-stopped\n    ports:\n      - "5432:5432"\n    environment:\n      - POSTGRES_USER=postgres\n      - POSTGRES_PASSWORD=postgres\n      - POSTGRES_DB=${name}\n    volumes:\n      - postgres-data:/var/lib/postgresql/data` : '',
        '',
        'volumes:',
        includeMongoDB ? '  mongo-data:' : '',
        includeORM ? '  postgres-data:' : '',
      ].filter(Boolean).join('\n');

      await writeFileAsync(path.join(projectDir, 'docker-compose.yml'), dockerCompose);
    }

    logger.info(`Microsserviço ${name} gerado com sucesso em ${projectDir}`);
  } catch (error) {
    logger.error('Erro ao gerar microsserviço', { error });
    throw error;
  }
}

export default {
  generateMicroservice,
};

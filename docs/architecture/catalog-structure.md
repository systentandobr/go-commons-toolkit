# Estrutura do Catálogo de Sistemas - Systentando ONE

Este documento detalha a arquitetura e implementação do Catálogo de Sistemas, componente central do ecossistema Systentando ONE que gerencia todos os produtos, suas integrações e métricas.

## Visão Geral

O Catálogo de Sistemas serve como registro central e hub de descoberta para todos os produtos no ecossistema Systentando. Ele permite:

1. **Registro e Descoberta**: Desenvolvedores podem registrar novos produtos e usuários podem descobri-los
2. **Integração**: Gerencia como os produtos se conectam e compartilham dados
3. **Métricas e Analytics**: Coleta e apresenta métricas de desempenho unificadas
4. **Governança**: Implementa políticas de qualidade e compatibilidade

## Modelo de Dados

### 1. Sistema/Produto

```typescript
interface Product {
  id: string;                // UUID único
  name: string;              // Nome do produto
  slug: string;              // URL-friendly name
  shortDescription: string;  // Descrição curta (max 140 caracteres)
  fullDescription: string;   // Descrição completa (markdown)
  category: ProductCategory; // Categoria do produto
  tags: string[];            // Tags para classificação e busca
  
  // Informações visuais
  logoUrl: string;           // URL do logo
  bannerUrl: string;         // URL da imagem de banner
  screenshots: Screenshot[]; // Capturas de tela
  
  // Links externos
  githubUrl?: string;        // Repositório no GitHub
  demoUrl?: string;          // URL de demonstração
  documentationUrl: string;  // Documentação
  
  // Autoria e contribuição
  authorId: string;          // ID do autor principal
  contributors: string[];    // IDs dos contribuidores
  
  // Métricas e status
  metrics: ProductMetrics;   // Métricas de desempenho
  status: ProductStatus;     // Status atual
  maturityLevel: MaturityLevel; // Nível de maturidade
  
  // Detalhes técnicos
  toolkitModules: string[];  // Módulos do toolkit utilizados
  apiEndpoints?: ApiEndpoint[]; // Endpoints de API disponíveis
  integrations: Integration[]; // Integrações com outros produtos
  
  // Informações de negócio
  businessProblemSolved: string; // Problema de negócio resolvido
  targetAudience: string[];  // Público-alvo
  features: ProductFeature[]; // Funcionalidades principais
  pricing?: PricingModel;    // Modelo de preço (opcional)
  
  // Versioning
  version: string;           // Versão atual (semver)
  changelog: ChangelogEntry[]; // Histórico de alterações
  
  // Datas
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
  publishedAt?: Date;        // Data de publicação
}

// Tipos auxiliares
type ProductCategory = 
  | 'WELLNESS'      // Bem-estar
  | 'PRODUCTIVITY'  // Produtividade
  | 'FINANCE'       // Finanças
  | 'NUTRITION'     // Nutrição
  | 'BUSINESS'      // Negócios
  | 'DEVELOPMENT'   // Desenvolvimento
  | 'EDUCATION'     // Educação
  | 'OTHER';        // Outros

type ProductStatus = 
  | 'DRAFT'         // Em elaboração
  | 'REVIEW'        // Em revisão
  | 'ALPHA'         // Alpha (teste interno)
  | 'BETA'          // Beta (teste público limitado)
  | 'PRODUCTION'    // Produção
  | 'DEPRECATED';   // Descontinuado

type MaturityLevel =
  | 'CONCEPT'       // Conceito/Ideia
  | 'PROTOTYPE'     // Protótipo funcional
  | 'MVP'           // Produto mínimo viável
  | 'GROWTH'        // Em crescimento
  | 'MATURE';       // Maduro

interface Screenshot {
  url: string;              // URL da imagem
  caption: string;          // Legenda
  order: number;            // Ordem de exibição
}

interface ApiEndpoint {
  path: string;             // Caminho do endpoint
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'; // Método HTTP
  description: string;      // Descrição
  authenticated: boolean;   // Requer autenticação
  parameters?: ApiParameter[]; // Parâmetros
  responses?: ApiResponse[]; // Respostas possíveis
}

interface ApiParameter {
  name: string;             // Nome do parâmetro
  type: string;             // Tipo de dados
  required: boolean;        // Obrigatório
  description: string;      // Descrição
}

interface ApiResponse {
  statusCode: number;       // Código HTTP
  description: string;      // Descrição
  schema?: string;          // Schema do formato de resposta
}

interface Integration {
  productId: string;        // ID do produto integrado
  description: string;      // Descrição da integração
  integrationType: 'DATA' | 'AUTH' | 'UI' | 'NOTIFICATION'; // Tipo
  status: 'PLANNED' | 'DEVELOPMENT' | 'ACTIVE' | 'DEPRECATED'; // Status
}

interface ProductFeature {
  name: string;             // Nome da funcionalidade
  description: string;      // Descrição
  iconUrl?: string;         // Ícone (opcional)
  status: 'PLANNED' | 'DEVELOPMENT' | 'ACTIVE'; // Status
}

interface PricingModel {
  type: 'FREE' | 'FREEMIUM' | 'SUBSCRIPTION' | 'ONE_TIME'; // Tipo
  basePrice?: number;       // Preço base (opcional)
  currency: string;         // Moeda (BRL, USD, etc.)
  billingCycle?: 'MONTHLY' | 'YEARLY'; // Ciclo de cobrança
  features: string[];       // Características incluídas
}

interface ChangelogEntry {
  version: string;          // Versão (semver)
  date: Date;               // Data da alteração
  description: string;      // Descrição das mudanças
  type: 'FEATURE' | 'BUGFIX' | 'IMPROVEMENT' | 'BREAKING'; // Tipo
}

interface ProductMetrics {
  totalUsers: number;        // Total de usuários
  activeUsers: number;       // Usuários ativos
  averageUsageTime: number;  // Tempo médio de uso (minutos)
  satisfactionScore: number; // Pontuação de satisfação (0-100)
  revenue: number;           // Receita gerada
  valuation: number;         // Valoração estimada
  contributionsCount: number; // Número de contribuições
  issuesOpen: number;        // Issues abertas
  issuesClosed: number;      // Issues fechadas
  deploymentFrequency: number; // Frequência de deployment (por mês)
  uptime: number;            // Disponibilidade (%)
}
```

### 2. Organização

```typescript
interface Organization {
  id: string;                // UUID único
  name: string;              // Nome da organização
  slug: string;              // URL-friendly name
  description: string;       // Descrição
  
  // Informações visuais
  logoUrl: string;           // URL do logotipo
  bannerUrl?: string;        // URL da imagem de banner
  
  // Links externos
  website?: string;          // Site institucional
  githubOrg?: string;        // Organização no GitHub
  
  // Composição
  members: OrganizationMember[]; // Membros e suas funções
  products: string[];        // IDs dos produtos
  
  // Assinaturas e uso
  subscriptions: Subscription[]; // Assinaturas de produtos
  usageLimits: UsageLimits;  // Limites de uso
  
  // Métricas
  metrics: OrganizationMetrics; // Métricas de desempenho
  
  // Datas
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}

interface OrganizationMember {
  developerId: string;       // ID do desenvolvedor
  role: OrgRole;             // Papel na organização
  permissions: Permission[]; // Permissões específicas
  joinedAt: Date;            // Data de entrada
}

type OrgRole =
  | 'OWNER'       // Proprietário
  | 'ADMIN'       // Administrador
  | 'MEMBER'      // Membro regular
  | 'GUEST';      // Convidado

type Permission =
  | 'MANAGE_MEMBERS'     // Gerenciar membros
  | 'MANAGE_PRODUCTS'    // Gerenciar produtos
  | 'BILLING'            // Acessar faturamento
  | 'VIEW_ANALYTICS';    // Ver análises

interface UsageLimits {
  maxUsers: number;         // Máximo de usuários
  maxStorage: number;       // Armazenamento máximo (MB)
  maxApiCalls: number;      // Máximo de chamadas API/dia
  features: string[];       // Recursos disponíveis
}

interface OrganizationMetrics {
  activeUsers: number;       // Usuários ativos
  productUsage: number;      // Uso total de produtos
  totalSpent: number;        // Valor total gasto
  businessImpact: number;    // Impacto nos negócios estimado
}
```

### 3. Desenvolvedor

```typescript
interface Developer {
  id: string;                // UUID único
  name: string;              // Nome completo
  username: string;          // Nome de usuário único
  email: string;             // Email (usado para autenticação)
  
  // Perfil profissional
  bio?: string;              // Biografia
  avatarUrl?: string;        // URL da imagem de perfil
  location?: string;         // Localização
  skills: string[];          // Habilidades técnicas
  
  // Links externos
  githubUrl?: string;        // Perfil do GitHub
  linkedinUrl?: string;      // Perfil do LinkedIn
  personalWebsite?: string;  // Site pessoal
  
  // Atividade e contribuições
  contributions: string[];   // IDs das contribuições
  organizations: string[];   // IDs das organizações
  products: string[];        // IDs dos produtos criados
  
  // Gamificação
  level: number;             // Nível atual
  experiencePoints: number;  // Pontos de experiência
  badges: UserBadge[];       // Distintivos conquistados
  
  // Equity
  equityTokens: number;      // Tokens de equity acumulados
  tokenHistory: TokenTransaction[]; // Histórico de tokens
  
  // Configurações
  preferences: UserPreferences; // Preferências
  
  // Métricas
  metrics: DeveloperMetrics; // Métricas de desempenho
  
  // Datas
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
  lastLoginAt?: Date;        // Último login
}

interface UserBadge {
  badgeId: string;           // ID do distintivo
  earnedAt: Date;            // Data de conquista
  highlighted: boolean;      // Destacado no perfil
}

interface TokenTransaction {
  amount: number;            // Quantidade de tokens
  type: 'EARNED' | 'SPENT' | 'TRANSFERRED'; // Tipo
  description: string;       // Descrição
  relatedEntityId?: string;  // ID da entidade relacionada
  timestamp: Date;           // Data e hora
}

interface UserPreferences {
  theme: 'LIGHT' | 'DARK' | 'SYSTEM'; // Tema
  emailNotifications: boolean; // Notificações por email
  pushNotifications: boolean;  // Notificações push
  displayLanguage: string;     // Idioma de exibição
  timezone: string;            // Fuso horário
  displayCalendar: boolean;    // Exibir calendário
}

interface DeveloperMetrics {
  contributionsCount: number;    // Total de contribuições
  impactScore: number;           // Pontuação de impacto
  activeDays: number;            // Dias ativos na plataforma
  challengesCompleted: number;   // Desafios concluídos
  mentorshipHours: number;       // Horas de mentoria
  responseTime: number;          // Tempo médio de resposta
  completionRate: number;        // Taxa de conclusão de tarefas
}
```

## APIs do Catálogo

### 1. API de Registro

Permite o registro e gerenciamento de produtos no catálogo.

```
POST /api/catalog/products - Registrar novo produto
PUT /api/catalog/products/:id - Atualizar produto existente
DELETE /api/catalog/products/:id - Remover produto
GET /api/catalog/products/:id - Obter detalhes do produto
GET /api/catalog/products - Listar produtos com filtros
```

### 2. API de Descoberta

Facilita a descoberta e exploração de produtos por usuários.

```
GET /api/discover/featured - Produtos em destaque
GET /api/discover/trending - Produtos em tendência
GET /api/discover/recommended - Recomendações personalizadas
GET /api/discover/search - Busca avançada
GET /api/discover/categories/:category - Produtos por categoria
```

### 3. API de Integração

Gerencia integrações entre produtos no ecossistema.

```
POST /api/integrations/connect - Conectar dois produtos
GET /api/integrations/products/:id - Listar integrações de um produto
POST /api/integrations/validate - Validar compatibilidade
GET /api/integrations/schema/:id - Obter schema de dados
```

### 4. API de Métricas

Coleta e expõe métricas de uso e desempenho.

```
POST /api/metrics/record - Registrar evento de métricas
GET /api/metrics/products/:id - Métricas de um produto
GET /api/metrics/organizations/:id - Métricas de uma organização
GET /api/metrics/dashboard - Dashboard de métricas consolidadas
GET /api/metrics/trends - Análise de tendências
```

## Interface do Catálogo

### 1. Explorador de Produtos

Interface principal para navegação e descoberta:

- Categorias navegáveis
- Filtros avançados
- Visualização em grade e lista
- Classificação por relevância, popularidade, data
- Cards interativos com informações resumidas

### 2. Página de Produto

Visualização detalhada de um produto:

- Header com banner, logo e informações essenciais
- Screenshots em carrossel
- Descrição e funcionalidades
- Métricas e estatísticas
- Integrações disponíveis
- Equipe de desenvolvimento
- Documentação e recursos
- Planos e preços

### 3. Dashboard de Desenvolvedores

Interface para desenvolvedores gerenciarem seus produtos:

- Lista dos produtos registrados
- Status de revisão e moderação
- Métricas de desempenho
- Integrações ativas
- Alertas e notificações
- Formulários de atualização

## Processos do Catálogo

### 1. Registro de Novo Produto

1. Desenvolvedor submete informações do produto
2. Sistema valida dados e requisitos mínimos
3. Revisão preliminar automática (segurança, qualidade)
4. Revisão manual por moderadores (opcional)
5. Produto publicado no catálogo
6. Notificação de interessados potenciais

### 2. Integração entre Produtos

1. Desenvolvedor solicita integração com outro produto
2. Sistema verifica compatibilidade técnica
3. Notificação ao desenvolvedor do produto alvo
4. Aprovação da integração
5. Configuração dos parâmetros de integração
6. Testes automáticos de validação
7. Publicação da integração no catálogo

### 3. Atualização de Produtos

1. Desenvolvedor submete atualização
2. Sistema compara com versão anterior
3. Validação de compatibilidade retroativa
4. Notificação aos usuários afetados
5. Publicação da atualização
6. Monitoramento de impacto

## Considerações Técnicas

### 1. Pesquisa e Descoberta

- Elasticsearch para busca avançada
- Algoritmos de recomendação baseados em:
  - Histórico de uso do usuário
  - Perfil e preferências
  - Comportamento de usuários similares
  - Tendências e popularidade

### 2. Performance e Escalabilidade

- Cache de produtos frequentemente acessados
- CDN para assets estáticos (imagens, documentação)
- Indexação otimizada para consultas comuns
- Paginação e carregamento lazy
- API rate limiting para proteger contra abusos

### 3. Validação e Qualidade

- Verificações automáticas de qualidade:
  - Segurança (vulnerabilidades conhecidas)
  - Desempenho (impacto em recursos)
  - Compatibilidade (integração com outros sistemas)
  - Documentação (completude e clareza)
- Sistema de avaliação e feedback de usuários
- Métricas de qualidade visíveis no catálogo

## Evolução Futura

### 1. Fase 1: Catálogo Básico

- Registro e listagem de produtos
- Perfis de desenvolvedores e organizações
- Métricas básicas de uso

### 2. Fase 2: Integração e Extensibilidade

- APIs para integração entre produtos
- Sistema de plugins e extensões
- Marketplace para componentes reutilizáveis

### 3. Fase 3: Inteligência e Personalização

- Recomendações personalizadas por IA
- Análise preditiva de tendências
- Automação de verificação de qualidade

### 4. Fase 4: Ecossistema Aberto

- APIs públicas para integração externa
- Federação com outros catálogos
- Governança comunitária
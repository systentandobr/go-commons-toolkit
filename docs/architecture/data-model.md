# Modelo de Dados - Systentando ONE

Este documento detalha o modelo de dados central que sustenta o ecossistema Systentando ONE, incluindo entidades, relacionamentos e estratégias de persistência.

## Entidades Principais

### Developer (Desenvolvedor)

```typescript
interface Developer {
  id: string;                // Identificador único
  name: string;              // Nome completo
  email: string;             // Email (usado para autenticação)
  skills: string[];          // Habilidades técnicas
  bio: string;               // Biografia profissional
  avatarUrl: string;         // URL da imagem de perfil
  githubUrl?: string;        // Perfil do GitHub (opcional)
  linkedinUrl?: string;      // Perfil do LinkedIn (opcional)
  contributions: Contribution[]; // Histórico de contribuições
  organizations: string[];   // IDs das organizações
  equityTokens: number;      // Tokens de equity acumulados
  projects: string[];        // IDs dos projetos próprios
  metrics: DeveloperMetrics; // Métricas de desempenho
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}

interface DeveloperMetrics {
  contributionsCount: number;    // Total de contribuições
  impactScore: number;           // Pontuação de impacto
  activeDays: number;            // Dias ativos na plataforma
  challengesCompleted: number;   // Desafios concluídos
  mentorshipHours: number;       // Horas de mentoria
}
```

### Organization (Organização)

```typescript
interface Organization {
  id: string;                // Identificador único
  name: string;              // Nome da organização
  description: string;       // Descrição
  logoUrl: string;           // URL do logotipo
  website?: string;          // Site institucional (opcional)
  members: OrganizationMember[]; // Membros e suas funções
  products: string[];        // IDs dos produtos
  subscriptions: Subscription[]; // Assinaturas de produtos
  metrics: OrganizationMetrics; // Métricas de desempenho
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}

interface OrganizationMember {
  developerId: string;       // ID do desenvolvedor
  role: 'ADMIN' | 'MEMBER';  // Papel na organização
  joinedAt: Date;            // Data de entrada
}

interface OrganizationMetrics {
  activeUsers: number;       // Usuários ativos
  productUsage: number;      // Uso total de produtos
  totalSpent: number;        // Valor total gasto
  businessImpact: number;    // Impacto nos negócios estimado
}
```

### Product (Produto/Sistema)

```typescript
interface Product {
  id: string;                // Identificador único
  name: string;              // Nome do produto
  description: string;       // Descrição detalhada
  shortDescription: string;  // Descrição curta
  category: string;          // Categoria (saúde, finanças, etc.)
  logoUrl: string;           // URL do logotipo
  bannerUrl: string;         // URL da imagem de banner
  githubUrl?: string;        // Repositório GitHub (opcional)
  demoUrl?: string;          // URL de demonstração (opcional)
  documentationUrl: string;  // URL da documentação
  authorId: string;          // ID do autor principal
  contributors: string[];    // IDs dos contribuidores
  toolkitModules: string[];  // Módulos do toolkit utilizados
  businessProblemSolved: string; // Problema de negócio resolvido
  targetAudience: string;    // Público-alvo
  features: ProductFeature[]; // Funcionalidades
  pricing?: PricingModel;    // Modelo de preço (opcional)
  metrics: ProductMetrics;   // Métricas de desempenho
  status: 'ALPHA' | 'BETA' | 'PRODUCTION'; // Status de desenvolvimento
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}

interface ProductFeature {
  name: string;              // Nome da funcionalidade
  description: string;       // Descrição
  iconUrl?: string;          // Ícone (opcional)
}

interface PricingModel {
  type: 'FREE' | 'FREEMIUM' | 'SUBSCRIPTION' | 'ONE_TIME'; // Tipo de preço
  basePrice?: number;        // Preço base (opcional)
  currency: string;          // Moeda (BRL, USD, etc.)
  billingCycle?: 'MONTHLY' | 'YEARLY'; // Ciclo de cobrança
  features: string[];        // Características incluídas
}

interface ProductMetrics {
  totalUsers: number;        // Total de usuários
  activeUsers: number;       // Usuários ativos
  averageUsageTime: number;  // Tempo médio de uso
  satisfactionScore: number; // Pontuação de satisfação
  revenue: number;           // Receita gerada
  valuation: number;         // Valoração estimada
}
```

### Contribution (Contribuição)

```typescript
interface Contribution {
  id: string;                // Identificador único
  developerId: string;       // ID do desenvolvedor
  productId: string;         // ID do produto
  type: 'CODE' | 'DOCUMENTATION' | 'DESIGN' | 'MENTORSHIP' | 'OTHER'; // Tipo
  description: string;       // Descrição da contribuição
  url?: string;              // URL da contribuição (GitHub, etc.)
  tokenValue: number;        // Valor em tokens de equity
  reviewedBy?: string;       // ID do revisor (opcional)
  status: 'PENDING' | 'APPROVED' | 'REJECTED'; // Status
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}
```

### Subscription (Assinatura)

```typescript
interface Subscription {
  id: string;                // Identificador único
  organizationId: string;    // ID da organização
  productId: string;         // ID do produto
  plan: string;              // Plano assinado
  startDate: Date;           // Data de início
  endDate?: Date;            // Data de término (opcional)
  price: number;             // Preço
  currency: string;          // Moeda
  status: 'ACTIVE' | 'CANCELED' | 'EXPIRED'; // Status
  paymentMethod: string;     // Método de pagamento
  autoRenew: boolean;        // Renovação automática
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}
```

## Estruturas de Dados Complementares

### Challenge (Desafio)

```typescript
interface Challenge {
  id: string;                // Identificador único
  title: string;             // Título
  description: string;       // Descrição detalhada
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'; // Dificuldade
  category: string;          // Categoria
  rewards: Reward[];         // Recompensas
  submissions: Submission[]; // Submissões
  startDate: Date;           // Data de início
  endDate?: Date;            // Data de término (opcional)
  status: 'DRAFT' | 'ACTIVE' | 'COMPLETED'; // Status
  createdBy: string;         // ID do criador
  createdAt: Date;           // Data de criação
  updatedAt: Date;           // Última atualização
}
```

### Badge (Distintivo)

```typescript
interface Badge {
  id: string;                // Identificador único
  name: string;              // Nome
  description: string;       // Descrição
  category: string;          // Categoria
  iconUrl: string;           // URL do ícone
  requirements: string;      // Requisitos para obtenção
  rarity: 'COMMON' | 'UNCOMMON' | 'RARE' | 'EPIC' | 'LEGENDARY'; // Raridade
  createdAt: Date;           // Data de criação
}
```

### UserBadge (Distintivo do Usuário)

```typescript
interface UserBadge {
  id: string;                // Identificador único
  badgeId: string;           // ID do distintivo
  developerId: string;       // ID do desenvolvedor
  awardedAt: Date;           // Data de conquista
}
```

## Diagrama de Relacionamento de Entidades (ERD)

```
Developer 1 --- * Contribution
Developer * --- * Organization (através de OrganizationMember)
Developer 1 --- * UserBadge
UserBadge * --- 1 Badge
Organization 1 --- * Subscription
Subscription * --- 1 Product
Product 1 --- * Contribution
Product 1 --- 1 Developer (autor)
Product * --- * Developer (contribuidores)
Challenge 1 --- * Submission
Submission * --- 1 Developer
```

## Estratégias de Persistência

### Bancos de Dados

1. **PostgreSQL**: Dados relacionais primários
   - Entidades principais (Developer, Organization, Product)
   - Relacionamentos complexos
   - Transações que exigem consistência

2. **MongoDB**: Dados não relacionais e expandíveis
   - Métricas e analytics
   - Logs de atividade
   - Documentos com estrutura variável

3. **Redis**: Cache e dados temporários
   - Sessões de usuário
   - Resultados de consultas frequentes
   - Filas de tarefas

### Estratégias de Modelagem

1. **Normalização vs. Desnormalização**
   - Dados frequentemente acessados juntos são desnormalizados
   - Dados com muitas relações mantêm normalização rigorosa

2. **Particionamento**
   - Dados organizacionais particionados por região
   - Métricas particionadas por período

3. **Histórico e Versionamento**
   - Mudanças em produtos mantêm histórico de versões
   - Contribuições são imutáveis após aprovação

## Considerações de Segurança

1. **Encriptação**
   - Dados pessoais criptografados em repouso
   - Transmissões sempre via TLS

2. **Isolamento de Dados**
   - Segregação de dados por organizações
   - Controle de acesso baseado em funções (RBAC)

3. **Auditoria**
   - Logs de todas as operações de escrita
   - Rastreamento de acessos a dados sensíveis

## Estratégia de Migração e Evolução

1. **Versionamento de Schema**
   - Migrations automatizadas para PostgreSQL
   - Evolução gradual de schemas em MongoDB

2. **Compatibilidade Retroativa**
   - APIs mantêm suporte a versões anteriores
   - Transformações automáticas para formatos legados

3. **Ambiente de Testes**
   - Cópias sanitizadas de dados de produção
   - Validação automática de migrations
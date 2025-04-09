# Estrutura de Dados do Usuário para o Agente Autônomo de E-commerce

Este documento define a estrutura de dados para armazenar e gerenciar informações individuais dos usuários no sistema do agente autônomo de e-commerce. Uma estrutura de dados bem planejada permitirá personalização, análise de desempenho e acompanhamento eficaz das interações e conversões.

## Visão Geral

A estrutura de dados do usuário foi projetada considerando os seguintes requisitos:

1. **Personalização**: Armazenar dados suficientes para personalizar interações
2. **Análise**: Permitir análises detalhadas de comportamento e conversão
3. **Privacidade**: Aderir às exigências da LGPD/GDPR
4. **Escalabilidade**: Suportar milhões de usuários sem degradação de desempenho
5. **Flexibilidade**: Adaptar-se a novos canais e tipos de interação

## Modelo de Dados Principal

### Usuário (User)

```json
{
  "id": "uuid-string",
  "phone": "+5511999999999",
  "email": "usuario@exemplo.com",
  "name": "Nome Completo",
  "created_at": "2023-05-10T14:30:00Z",
  "last_active_at": "2023-05-25T09:15:32Z",
  "status": "active",
  "consent": {
    "marketing": true,
    "data_processing": true,
    "third_party_sharing": false,
    "last_updated_at": "2023-05-10T14:30:00Z"
  },
  "profile": {
    "birth_date": "1985-04-15",
    "gender": "F",
    "location": {
      "city": "São Paulo",
      "state": "SP",
      "country": "Brasil",
      "postal_code": "01310-200"
    },
    "language": "pt-BR",
    "preferences": {
      "communication_channel": "whatsapp",
      "categories_of_interest": ["eletrônicos", "moda", "casa"],
      "price_sensitivity": "medium",
      "shopping_frequency": "monthly",
      "notification_preferences": {
        "promotions": true,
        "order_updates": true,
        "recommendations": true
      }
    }
  },
  "segmentation": {
    "customer_value_tier": "gold",
    "lifecycle_stage": "active",
    "acquisition_source": "facebook_ad",
    "persona": "tech_enthusiast",
    "churn_risk": "low",
    "upsell_potential": "high"
  },
  "metrics": {
    "lifetime_value": 2750.50,
    "average_order_value": 458.40,
    "orders_count": 6,
    "cart_abandonment_rate": 0.25,
    "average_session_duration": 340,
    "nps_score": 9,
    "last_nps_date": "2023-04-12T10:15:00Z"
  }
}
```

### Sessão (Session)

```json
{
  "id": "uuid-string",
  "user_id": "user-uuid-reference",
  "channel": "whatsapp",
  "device_info": {
    "type": "smartphone",
    "os": "android",
    "browser": null,
    "app_version": null
  },
  "started_at": "2023-05-25T09:00:00Z",
  "ended_at": "2023-05-25T09:15:32Z",
  "duration": 932,
  "session_state": {
    "stage": "checkout",
    "last_intent": "payment_selection",
    "context": {
      "products_viewed": ["prod-123", "prod-456"],
      "cart_id": "cart-789",
      "last_category": "smartphones",
      "search_query": "iphone 13"
    }
  },
  "location_data": {
    "ip_address": "192.168.1.1",
    "geo_location": {
      "latitude": -23.550520,
      "longitude": -46.633308,
      "accuracy": 100
    }
  },
  "source": {
    "utm_source": "email",
    "utm_medium": "promotion",
    "utm_campaign": "summer_sale",
    "referrer": "email_link"
  }
}
```

### Interação (Interaction)

```json
{
  "id": "uuid-string",
  "session_id": "session-uuid-reference",
  "user_id": "user-uuid-reference",
  "timestamp": "2023-05-25T09:05:22Z",
  "channel": "whatsapp",
  "type": "message",
  "direction": "incoming",
  "content": {
    "text": "Quero ver smartphones até R$2000",
    "attachments": [],
    "structured_data": null
  },
  "metadata": {
    "message_id": "whatsapp-msg-123456",
    "status": "delivered"
  },
  "nlp_data": {
    "intent": "product_search",
    "entities": [
      {
        "type": "product_category",
        "value": "smartphone",
        "confidence": 0.95
      },
      {
        "type": "price_range",
        "value": {
          "max": 2000
        },
        "confidence": 0.87
      }
    ],
    "sentiment": {
      "score": 0.2,
      "magnitude": 0.4,
      "label": "neutral"
    }
  },
  "agent_response": {
    "id": "response-uuid",
    "timestamp": "2023-05-25T09:05:25Z",
    "response_time": 3.2,
    "type": "text_with_options",
    "content": {
      "text": "Encontrei estas opções de smartphones até R$2000:",
      "options": ["Ver Motorola", "Ver Samsung", "Ver Xiaomi"]
    },
    "products_shown": ["prod-111", "prod-222", "prod-333"],
    "techniques_used": ["social_proof", "categorization"]
  }
}
```

### Carrinho (Cart)

```json
{
  "id": "uuid-string",
  "user_id": "user-uuid-reference",
  "session_id": "session-uuid-reference",
  "status": "active",
  "created_at": "2023-05-25T09:08:10Z",
  "updated_at": "2023-05-25T09:12:45Z",
  "items": [
    {
      "product_id": "prod-111",
      "variant_id": "var-222",
      "name": "Smartphone XYZ",
      "quantity": 1,
      "unit_price": 1899.00,
      "total_price": 1899.00,
      "added_at": "2023-05-25T09:10:30Z",
      "attributes": {
        "color": "preto",
        "storage": "128GB"
      }
    }
  ],
  "totals": {
    "subtotal": 1899.00,
    "shipping": 0.00,
    "discount": 0.00,
    "tax": 0.00,
    "grand_total": 1899.00
  },
  "checkout_url": "https://loja.exemplo.com/checkout/cart-789",
  "applied_promotions": [],
  "metadata": {
    "has_abandoned": false,
    "recovery_attempts": 0,
    "source": "whatsapp",
    "suggested_by_agent": true
  }
}
```

### Pedido (Order)

```json
{
  "id": "uuid-string",
  "order_number": "ORDER-12345",
  "user_id": "user-uuid-reference",
  "cart_id": "cart-uuid-reference",
  "status": "processing",
  "created_at": "2023-05-25T09:20:00Z",
  "updated_at": "2023-05-25T09:22:30Z",
  "items": [
    {
      "product_id": "prod-111",
      "variant_id": "var-222",
      "name": "Smartphone XYZ",
      "quantity": 1,
      "unit_price": 1899.00,
      "total_price": 1899.00,
      "attributes": {
        "color": "preto",
        "storage": "128GB"
      }
    }
  ],
  "totals": {
    "subtotal": 1899.00,
    "shipping": 0.00,
    "discount": 0.00,
    "tax": 0.00,
    "grand_total": 1899.00
  },
  "shipping_address": {
    "name": "Nome Completo",
    "street": "Rua Exemplo, 123",
    "complement": "Apto 45",
    "district": "Bairro",
    "city": "São Paulo",
    "state": "SP",
    "postal_code": "01310-200",
    "country": "Brasil"
  },
  "shipping_method": {
    "code": "express",
    "name": "Entrega Expressa",
    "estimated_delivery": "2023-05-27T18:00:00Z",
    "tracking_number": "TRACK123456789",
    "tracking_url": "https://rastreio.exemplo.com/TRACK123456789"
  },
  "payment": {
    "method": "credit_card",
    "status": "approved",
    "installments": 3,
    "card_info": {
      "brand": "visa",
      "last_digits": "1234",
      "holder_name": "NOME IMPRESSO"
    },
    "transaction_id": "tx-987654"
  },
  "notes": "",
  "conversion": {
    "source": "whatsapp",
    "campaign": "summer_sale",
    "agent_assisted": true,
    "techniques_used": ["scarcity", "social_proof"],
    "time_to_convert": 15.5
  }
}
```

### Métricas do Usuário (UserMetrics)

```json
{
  "user_id": "user-uuid-reference",
  "updated_at": "2023-05-25T10:00:00Z",
  "shopping_behavior": {
    "favorite_categories": [
      {"category": "smartphones", "view_count": 45, "purchase_count": 2},
      {"category": "acessórios", "view_count": 23, "purchase_count": 3}
    ],
    "favorite_brands": [
      {"brand": "samsung", "view_count": 28, "purchase_count": 1},
      {"brand": "apple", "view_count": 17, "purchase_count": 1}
    ],
    "price_range": {
      "min": 59.90,
      "max": 1899.00,
      "average": 623.45
    },
    "purchase_frequency": {
      "last_30_days": 1,
      "last_90_days": 2,
      "last_365_days": 6
    },
    "payment_methods": [
      {"method": "credit_card", "frequency": 5},
      {"method": "pix", "frequency": 1}
    ]
  },
  "interaction_metrics": {
    "total_interactions": 127,
    "response_rate": 0.95,
    "average_session_duration": 340,
    "average_messages_per_session": 8.5,
    "preferred_interaction_time": {
      "day_of_week": "thursday",
      "time_of_day": "evening"
    },
    "conversation_topics": [
      {"topic": "product_inquiry", "frequency": 45},
      {"topic": "order_status", "frequency": 15},
      {"topic": "price_check", "frequency": 30}
    ]
  },
  "conversion_metrics": {
    "view_to_cart_rate": 0.12,
    "cart_to_order_rate": 0.75,
    "overall_conversion_rate": 0.09,
    "average_order_value": 458.40,
    "lifetime_value": 2750.50,
    "first_order_date": "2022-11-20T14:30:00Z",
    "last_order_date": "2023-05-10T11:45:00Z"
  },
  "engagement_scores": {
    "recency": 0.8,
    "frequency": 0.6,
    "monetary": 0.7,
    "nps": 9,
    "satisfaction": 4.8,
    "product_review_rate": 0.5,
    "referral_count": 2,
    "loyalty_points": 450
  },
  "persuasion_effectiveness": {
    "most_effective_techniques": [
      {"technique": "social_proof", "conversion_rate": 0.15},
      {"technique": "scarcity", "conversion_rate": 0.12},
      {"technique": "authority", "conversion_rate": 0.09}
    ],
    "most_effective_incentives": [
      {"incentive": "free_shipping", "conversion_rate": 0.18},
      {"incentive": "discount_10percent", "conversion_rate": 0.14}
    ],
    "objection_patterns": [
      {"objection": "price", "frequency": 5},
      {"objection": "shipping_time", "frequency": 3}
    ]
  }
}
```

## Estrutura do Banco de Dados

### Abordagem de Armazenamento

Recomendamos uma abordagem híbrida para armazenamento de dados:

1. **Banco Relacional (PostgreSQL)**
   - Dados estruturados de usuários, pedidos, produtos
   - Relacionamentos entre entidades
   - Dados transacionais e financeiros

2. **Banco NoSQL (MongoDB)**
   - Interações e conversas
   - Dados comportamentais e de análise
   - Métricas e perfis de usuário (documentos aninhados)

3. **Banco de Dados em Memória (Redis)**
   - Estado da sessão atual
   - Carrinhos ativos
   - Cache de perfil de usuário para acesso rápido
   - Filas de atendimento

4. **Data Warehouse (Snowflake/BigQuery)**
   - Dados agregados para análise
   - Histórico completo para machine learning
   - Backups de longo prazo

### Diagrama Entidade-Relacionamento Simplificado

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │
│    Users     │1───┬┤  Sessions    │1───┬┤ Interactions │
│              │    N│              │    N│              │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │1                                        
       │                                         
       │N                                        
┌──────▼───────┐     ┌──────────────┐     ┌──────────────┐
│              │1    │              │1    │              │
│    Carts     ├────┬┤    Orders    ├────┬┤OrderItems    │
│              │    N│              │    N│              │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │1                     
                            │                      
                            │N                     
                     ┌──────▼───────┐              
                     │              │              
                     │Transactions  │              
                     │              │              
                     └──────────────┘              
```

## Políticas de Acesso e Segurança

### Níveis de Acesso

1. **Operação do Agente** (Acesso Limitado)
   - Atributos básicos de usuário
   - Histórico de interações recentes
   - Carrinho atual e status de pedidos
   - Métricas de conversão

2. **Análise e Business Intelligence** (Acesso Amplo)
   - Dados agregados e anônimos
   - Métricas de performance
   - Padrões de comportamento
   - Estatísticas de conversão

3. **Administração** (Acesso Total)
   - Todos os dados individuais
   - Configurações de sistema
   - Logs de auditoria
   - Dados financeiros

### Medidas de Proteção

1. **Criptografia**
   - Dados em repouso criptografados (AES-256)
   - Comunicação via TLS 1.3
   - Hash para senhas e dados sensíveis

2. **Anonimização para Análise**
   - Tokenização de identificadores pessoais
   - Remoção de dados diretamente identificáveis
   - Agregação para relatórios gerais

3. **Auditoria e Monitoramento**
   - Logs de todas as acessos a dados
   - Alertas para comportamentos suspeitos
   - Revisão periódica de permissões

4. **Conformidade LGPD/GDPR**
   - Regras de retenção e exclusão
   - Mecanismo de consentimento
   - Portabilidade de dados

## Modelo de Persistência e Ciclo de Vida

### Retenção de Dados

1. **Dados Ativos**
   - Perfil de usuário: Enquanto conta ativa
   - Interações: 12 meses para uso operacional
   - Pedidos: 5 anos (requisitos fiscais)
   - Métricas: 2 anos para personalização

2. **Dados Arquivados**
   - Interações antigas: 3 anos
   - Pedidos antigos: 10 anos
   - Perfis inativos: 2 anos após inatividade

3. **Exclusão Programada**
   - Dados de navegação: 90 dias
   - Carrinhos abandonados: 180 dias
   - Tokens e sessões: 24 horas após expiração

### Gestão de Consentimento

```json
{
  "user_id": "user-uuid-reference",
  "consents": [
    {
      "type": "data_processing",
      "granted": true,
      "timestamp": "2023-01-15T10:30:00Z",
      "expiration": null,
      "version": "1.2",
      "source": "whatsapp_opt_in"
    },
    {
      "type": "marketing",
      "granted": true,
      "timestamp": "2023-01-15T10:30:00Z",
      "expiration": "2024-01-15T10:30:00Z",
      "version": "1.1",
      "source": "whatsapp_opt_in"
    },
    {
      "type": "third_party_sharing",
      "granted": false,
      "timestamp": "2023-01-15T10:30:00Z",
      "expiration": null,
      "version": "1.0",
      "source": "whatsapp_opt_in"
    }
  ],
  "consent_history": [
    {
      "type": "marketing",
      "action": "granted",
      "timestamp": "2022-06-10T14:20:00Z",
      "version": "1.0",
      "source": "website_registration"
    },
    {
      "type": "marketing",
      "action": "updated",
      "timestamp": "2023-01-15T10:30:00Z",
      "version": "1.1",
      "source": "whatsapp_opt_in"
    }
  ],
  "data_subject_requests": [
    {
      "type": "access",
      "status": "completed",
      "requested_at": "2023-02-10T09:15:00Z",
      "completed_at": "2023-02-11T14:30:00Z",
      "reference_id": "dsr-12345"
    }
  ]
}
```

## Estratégia de Sincronização e Integração

### APIs e Interfaces

1. **API RESTful**
   - Endpoints para CRUD de usuários
   - Gestão de sessões e carrinhos
   - Histórico de pedidos e interações

2. **Webhooks**
   - Notificações de eventos relevantes
   - Integração com sistemas externos
   - Atualizações em tempo real

3. **Streaming de Eventos**
   - Eventos de usuário (Kafka/RabbitMQ)
   - Atualização de métricas em tempo real
   - Sincronização entre componentes

### Integrações Externas

1. **CRM**
   - Perfil unificado do cliente
   - Histórico de compras e interações
   - Oportunidades de venda

2. **Plataforma de E-commerce**
   - Catálogo de produtos
   - Gestão de estoque
   - Processamento de pedidos

3. **Sistema de Pagamentos**
   - Processamento de transações
   - Verificação de fraude
   - Confirmação de pagamentos

4. **Logística**
   - Status de entrega
   - Rastreamento de pedidos
   - Gestão de devoluções

## Sistema de Fila de Atendimento

### Modelo de Fila

```json
{
  "id": "queue-uuid-string",
  "name": "Fila Principal",
  "description": "Fila para atendimento de vendas via WhatsApp",
  "created_at": "2023-01-01T00:00:00Z",
  "status": "active",
  "settings": {
    "max_waiting_time": 300,
    "priority_rules": [
      {"criterion": "cart_value", "min_value": 1000, "priority_score": 10},
      {"criterion": "customer_tier", "value": "gold", "priority_score": 15},
      {"criterion": "waiting_time", "per_minute": 1, "max_score": 20}
    ],
    "escalation_rules": [
      {"condition": "waiting_time > 10", "action": "escalate_to_human"},
      {"condition": "sentiment < -0.5", "action": "escalate_to_human"}
    ],
    "business_hours": [
      {"day": "monday", "start": "08:00", "end": "18:00"},
      {"day": "tuesday", "start": "08:00", "end": "18:00"},
      {"day": "wednesday", "start": "08:00", "end": "18:00"},
      {"day": "thursday", "start": "08:00", "end": "18:00"},
      {"day": "friday", "start": "08:00", "end": "18:00"}
    ]
  },
  "metrics": {
    "current_length": 12,
    "average_waiting_time": 180,
    "average_handling_time": 540,
    "abandonment_rate": 0.05,
    "resolution_rate": 0.85
  }
}
```

### Item na Fila

```json
{
  "id": "queue-item-uuid",
  "queue_id": "queue-uuid-reference",
  "user_id": "user-uuid-reference",
  "session_id": "session-uuid-reference",
  "priority_score": 75,
  "status": "waiting",
  "created_at": "2023-05-25T09:30:00Z",
  "last_updated_at": "2023-05-25T09:35:00Z",
  "waiting_time": 300,
  "agent_assigned": null,
  "data": {
    "channel": "whatsapp",
    "initial_message": "Preciso de ajuda com meu pedido",
    "detected_intent": "order_issue",
    "detected_sentiment": -0.2,
    "context": {
      "last_order_id": "order-uuid-reference",
      "cart_value": 0,
      "customer_tier": "silver"
    }
  },
  "history": [
    {
      "timestamp": "2023-05-25T09:30:00Z",
      "event": "created",
      "details": "Added to queue with priority 70"
    },
    {
      "timestamp": "2023-05-25T09:33:00Z",
      "event": "priority_updated",
      "details": "Priority increased to 73 due to waiting time"
    },
    {
      "timestamp": "2023-05-25T09:35:00Z",
      "event": "priority_updated",
      "details": "Priority increased to 75 due to waiting time"
    }
  ]
}
```

### Operador/Agente

```json
{
  "id": "agent-uuid-string",
  "type": "bot",
  "name": "Agente de Vendas",
  "status": "online",
  "capabilities": ["product_information", "order_processing", "payment_handling"],
  "active_since": "2023-05-25T08:00:00Z",
  "current_load": 8,
  "max_capacity": 20,
  "assigned_conversations": ["session-uuid-1", "session-uuid-2"],
  "performance": {
    "average_handling_time": 420,
    "resolution_rate": 0.88,
    "customer_satisfaction": 4.7,
    "conversion_rate": 0.15
  },
  "settings": {
    "max_concurrent_sessions": 20,
    "auto_assignment": true,
    "specialties": ["electronics", "home_appliances"]
  }
}
```

## Análise e Inteligência

### Agregações e Relatórios

1. **Relatórios de Conversão**
   - Taxas por canal, produto, segmento
   - Análise temporal (hora do dia, dia da semana)
   - Impacto de técnicas de persuasão

2. **Análise de Comportamento**
   - Padrões de navegação e interação
   - Sequências que levam à conversão
   - Pontos de abandono comuns

3. **Segmentação Dinâmica**
   - Clusters baseados em comportamento
   - Predição de próxima compra
   - Identificação de perfis de alto valor

### Modelos Preditivos

1. **Propensão a Compra**
   - Probabilidade de conversão
   - Previsão de próximo produto
   - Momento ideal para abordagem

2. **Risco de Abandono**
   - Detecção precoce de sinais de abandono
   - Gatilhos para intervenção
   - Incentivos personalizados

3. **Valor Vitalício (LTV)**
   - Projeção de receita futura
   - Segmentação por potencial
   - Otimização de investimento por cliente

## Implementação Técnica

### Tecnologias Recomendadas

1. **Armazenamento de Dados**
   - PostgreSQL (dados relacionais)
   - MongoDB (dados de interação)
   - Redis (cache e filas)
   - S3/GCS (mídia e anexos)

2. **Backend e APIs**
   - Python com FastAPI/Django
   - Node.js com Express
   - GraphQL para consultas complexas

3. **Processamento em Tempo Real**
   - Kafka/RabbitMQ para eventos
   - Spark para processamento distribuído
   - Flink para streaming de eventos

4. **Machine Learning e Análise**
   - TensorFlow/PyTorch para modelos
   - scikit-learn para análises simples
   - Pandas para manipulação de dados
   - Metabase/Tableau para visualização

### Considerações de Implementação

1. **Escalabilidade**
   - Design para sharding horizontal
   - Particionamento por usuário ou região
   - Cache hierárquico para perfis ativos

2. **Performance**
   - Índices otimizados para consultas frequentes
   - Denormalização estratégica para leituras
   - Compressão para dados históricos

3. **Disponibilidade**
   - Replicação multi-região
   - Backups incrementais programados
   - Estratégia de disaster recovery

## Plano de Implementação

### Fase 1: Fundação (Mês 1-2)

- Implementação do modelo básico de usuário
- Integração com WhatsApp e plataforma de e-commerce
- Sistema simples de fila de atendimento
- Captura de interações e análise básica

### Fase 2: Análise e Personalização (Mês 3-4)

- Expansão do modelo de métricas e comportamento
- Implementação de segmentação dinâmica
- Integração com CRM e sistemas de pagamento
- Dashboards iniciais de análise

### Fase 3: Inteligência e Automação (Mês 5-6)

- Modelos preditivos para propensão e LTV
- Personalização avançada baseada em comportamento
- Sistema avançado de fila com priorização
- Integração completa com logística e pós-venda

### Fase 4: Otimização Contínua (Mês 7+)

- Refinamento de modelos com feedback real
- Expansão para novos canais de atendimento
- Automação avançada de campanhas
- Predição e prevenção de abandono

# Sistema de Gerenciamento de Fila de Atendimento

Este documento descreve o sistema de gerenciamento de fila para o agente autônomo de e-commerce, detalhando como as interações serão priorizadas, processadas e encaminhadas.

## Visão Geral

O sistema de fila inteligente é responsável por:

1. Priorizar interações com base em potencial de conversão e urgência
2. Distribuir carga entre instâncias do agente
3. Gerenciar transferências para atendimento humano quando necessário
4. Coletar métricas de desempenho e tempo de resposta

## Arquitetura do Sistema de Fila

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    SISTEMA DE FILA                          │
│                                                             │
├─────────────────┬─────────────────────┬───────────────────┐ │
│  Classificador  │    Distribuidor     │  Escalonador      │ │
│  de Prioridade  │    de Carga         │  para Humanos     │ │
├─────────────────┼─────────────────────┼───────────────────┤ │
│  • Scoring      │  • Load Balancing   │  • Detecção de    │ │
│  • Categorização│  • Monitoramento    │    necessidade    │ │
│  • Reordenação  │  • Auto-scaling     │  • Transferência  │ │
└─────────────────┴─────────────────────┴───────────────────┘ │
                            │                                  │
        ┌─────────────────────────────────────────┐           │
        │         PROCESSADOR DE FILA             │           │
        └─────────────────────────────────────────┘           │
                            │                                  │
┌─────────────────┬─────────────────────┬───────────────────┐ │
│  Monitores      │   Agentes           │     Atendentes    │ │
│  de Fila        │   Autônomos         │     Humanos       │ │
├─────────────────┼─────────────────────┼───────────────────┤ │
│  • Dashboard    │  • Instâncias de    │  • Interface de   │ │
│  • Alertas      │    Agentes IA       │    atendimento    │ │
│  • Métricas     │  • Pool de recursos │  • Histórico      │ │
└─────────────────┴─────────────────────┴───────────────────┘ │
                                                               │
┌───────────────────────────────────────────────────────────┐ │
│                                                           │ │
│                ARMAZENAMENTO DE DADOS                     │ │
│                                                           │ │
├─────────────────┬─────────────────────┬─────────────────┐ │ │
│  Fila Ativa     │ Histórico de Filas  │ Métricas e KPIs │ │ │
└─────────────────┴─────────────────────┴─────────────────┘ │ │
                                                             │ │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principais

### 1. Classificador de Prioridade

Este componente avalia cada nova interação e atribui um score de prioridade baseado em múltiplos fatores:

#### Fatores de Priorização:

1. **Potencial de Venda**
   - Histórico de compras do cliente
   - Valor médio de pedidos anteriores
   - Recência da última interação
   - Fase atual da jornada de compra

2. **Urgência da Solicitação**
   - Análise de palavras-chave de urgência
   - Contato relacionado a pedido já realizado
   - Tempo do cliente na plataforma

3. **Contexto da Interação**
   - Origem do contato (anúncio, site, indicação)
   - Produtos específicos mencionados
   - Campanhas ativas relacionadas

4. **Perfil do Cliente**
   - Status de fidelidade
   - Frequência de compras
   - Comportamento de navegação prévio

#### Algoritmo de Pontuação:

```python
def calculate_priority_score(customer_data, message_data, context_data):
    # Base score
    score = 50
    
    # Purchase potential (0-30 points)
    if customer_data.get('purchase_history'):
        score += min(30, customer_data['lifetime_value'] / 100)
    else:
        # New customer bonus
        score += 15
    
    # Urgency factors (0-25 points)
    urgency_keywords = ['urgente', 'rápido', 'hoje', 'agora', 'problema', 'erro']
    urgency_score = sum(2 for keyword in urgency_keywords if keyword in message_data['text'].lower())
    score += min(25, urgency_score * 5)
    
    # Order status inquiries get priority
    if 'pedido' in message_data['text'].lower() and 'status' in message_data['text'].lower():
        score += 15
    
    # Context factors (0-25 points)
    if context_data.get('source') == 'paid_ad':
        score += 10
    
    if context_data.get('cart_value', 0) > 500:
        score += 15
    
    # Waiting time adjustment (0-20 points)
    wait_time_minutes = (datetime.now() - context_data.get('first_contact_time')).total_seconds() / 60
    score += min(20, wait_time_minutes / 2)
    
    return min(100, score)  # Cap at 100
```

#### Categorias de Prioridade:

- **Crítica** (90-100): Atendimento imediato
- **Alta** (75-89): Próximo na fila
- **Média** (50-74): Atendimento normal
- **Baixa** (0-49): Atendimento quando disponível

### 2. Distribuidor de Carga

Responsável por alocar recursos de forma eficiente entre os diferentes níveis de prioridade e instâncias de agentes.

#### Principais Funcionalidades:

1. **Balanceamento de Carga**
   - Distribuição de interações entre instâncias disponíveis
   - Monitoramento de carga por instância
   - Redistribuição em caso de sobrecarga

2. **Auto-scaling**
   - Monitoramento de métricas de fila (tamanho, tempo de espera)
   - Provisionamento automático de novas instâncias
   - Desativação de instâncias ociosas

3. **Reserva de Recursos**
   - Garantia de capacidade mínima para casos críticos
   - Ajuste dinâmico de alocação baseado em padrões de tráfego
   - Prevenção de monopolização de recursos

#### Algoritmo de Distribuição:

```python
def distribute_interactions(queue, available_agents):
    # Sort queue by priority score (descending)
    sorted_queue = sorted(queue, key=lambda x: x['priority_score'], reverse=True)
    
    # Group agents by capability/specialization
    agent_groups = group_agents_by_capability(available_agents)
    
    assignments = []
    
    # First pass: assign high priority items to specialized agents
    for interaction in [i for i in sorted_queue if i['priority_score'] >= 75]:
        # Determine required agent capabilities
        required_capabilities = determine_required_capabilities(interaction)
        
        # Find best matching agent
        best_agent = find_best_agent_match(interaction, agent_groups, required_capabilities)
        
        if best_agent:
            assignments.append((interaction, best_agent))
            agent_groups = update_agent_availability(agent_groups, best_agent)
            sorted_queue.remove(interaction)
    
    # Second pass: assign remaining items to available agents
    for interaction in sorted_queue:
        # Find any available agent
        available_agent = find_available_agent(agent_groups)
        
        if available_agent:
            assignments.append((interaction, available_agent))
            agent_groups = update_agent_availability(agent_groups, available_agent)
    
    return assignments
```

### 3. Escalonador para Humanos

Este componente identifica quando uma interação precisa ser transferida para atendimento humano.

#### Critérios para Escalonamento:

1. **Complexidade Técnica**
   - Problemas que o agente não está programado para resolver
   - Questões ambíguas ou sem padrão reconhecível
   - Solicitações muito específicas ou incomuns

2. **Estado Emocional do Cliente**
   - Detecção de frustração ou insatisfação
   - Linguagem agressiva ou irritada
   - Menção explícita de desejo de falar com humano

3. **Valor da Oportunidade**
   - Potencial de venda de alto valor
   - Cliente VIP ou de alto valor
   - Oportunidade de upsell significativa

4. **Sensitividade do Assunto**
   - Questões relacionadas a pagamentos recusados
   - Problemas de privacidade ou segurança
   - Reclamações ou devoluções

#### Algoritmo de Decisão para Escalonamento:

```python
def should_escalate_to_human(interaction_data, conversation_history, customer_profile):
    # Check for explicit request for human
    if contains_human_request(interaction_data['message']):
        return True, "explicit_request"
    
    # Check for complex technical issues
    if complexity_score(conversation_history) > 0.7:
        return True, "technical_complexity"
    
    # Check for emotional distress
    sentiment_score = analyze_sentiment(interaction_data['message'])
    if sentiment_score < -0.5:
        return True, "customer_distress"
    
    # Check for high-value opportunity
    if (customer_profile.get('lifetime_value', 0) > 5000 or 
        interaction_data.get('estimated_cart_value', 0) > 2000):
        return True, "high_value_opportunity"
    
    # Check for sensitive topics
    if contains_sensitive_topics(interaction_data['message']):
        return True, "sensitive_topic"
    
    # Check for repeated misunderstandings
    if count_clarification_requests(conversation_history) >= 3:
        return True, "repeated_misunderstanding"
    
    return False, None
```

#### Processo de Transferência:

1. **Preparação de Contexto**
   - Resumo da conversa até o momento
   - Identificação do problema principal
   - Tentativas já realizadas pelo agente

2. **Notificação ao Cliente**
   - Explicação clara sobre a transferência
   - Estimativa de tempo de espera
   - Opção de agendamento (se espera longa)

3. **Seleção de Atendente**
   - Correspondência com especialidade necessária
   - Consideração de histórico de interações prévias
   - Disponibilidade e carga atual

## Estrutura de Dados da Fila

### Modelo de Dados de Item na Fila

```python
class QueueItem:
    id: str  # Identificador único
    customer_id: str  # ID do cliente
    priority_score: float  # Pontuação de 0-100
    entry_time: datetime  # Momento de entrada na fila
    last_update_time: datetime  # Última atualização
    source: str  # Origem da interação (whatsapp, web, etc)
    initial_message: str  # Primeira mensagem recebida
    intent: str  # Intenção detectada
    assigned_to: Optional[str]  # ID do agente atribuído
    status: QueueStatus  # Enum (waiting, processing, escalated, completed)
    escalation_reason: Optional[str]  # Razão se escalonado
    estimated_response_time: int  # Tempo estimado em segundos
    tags: List[str]  # Tags relevantes
    metadata: Dict[str, Any]  # Dados adicionais específicos
```

### Modelo de Dados de Agente

```python
class Agent:
    id: str  # Identificador único
    type: AgentType  # Enum (ai, human)
    status: AgentStatus  # Enum (available, busy, offline)
    capabilities: List[str]  # Habilidades especiais
    current_load: int  # Número de interações simultâneas
    max_capacity: int  # Capacidade máxima
    performance_metrics: Dict[str, float]  # Métricas de desempenho
    specializations: List[str]  # Áreas de especialização
    languages: List[str]  # Idiomas suportados
    shift_end_time: Optional[datetime]  # Fim do turno (para humanos)
```

## Operações da Fila

### 1. Enfileiramento

Processo de adicionar uma nova interação à fila:

```python
def enqueue_interaction(customer_id, message, context_data):
    # Create unique ID
    interaction_id = generate_unique_id()
    
    # Fetch customer data
    customer_data = fetch_customer_data(customer_id)
    
    # Calculate priority
    priority_score = calculate_priority_score(customer_data, message, context_data)
    
    # Determine intent
    intent = detect_intent(message)
    
    # Create queue item
    queue_item = QueueItem(
        id=interaction_id,
        customer_id=customer_id,
        priority_score=priority_score,
        entry_time=datetime.now(),
        last_update_time=datetime.now(),
        source=context_data.get('source', 'unknown'),
        initial_message=message,
        intent=intent,
        assigned_to=None,
        status=QueueStatus.WAITING,
        escalation_reason=None,
        estimated_response_time=estimate_response_time(priority_score, get_queue_length()),
        tags=generate_tags(message, intent, customer_data),
        metadata=context_data
    )
    
    # Add to database
    store_queue_item(queue_item)
    
    # Notify monitoring system
    notify_new_interaction(queue_item)
    
    return interaction_id
```

### 2. Processamento

Lógica para atribuir e processar itens da fila:

```python
def process_queue(available_agents):
    # Get all waiting items
    waiting_items = get_waiting_queue_items()
    
    # Get assignments from distributor
    assignments = distribute_interactions(waiting_items, available_agents)
    
    for interaction, agent in assignments:
        # Update item status
        update_queue_item_status(
            interaction_id=interaction['id'],
            new_status=QueueStatus.PROCESSING,
            assigned_to=agent['id']
        )
        
        # Send to agent for processing
        if agent['type'] == AgentType.AI:
            send_to_ai_agent(interaction, agent)
        else:
            send_to_human_agent(interaction, agent)
        
        # Update metrics
        update_queue_metrics(interaction, 'assigned')
```

### 3. Escalonamento

Processo de transferência para atendimento humano:

```python
def escalate_to_human(interaction_id, reason, conversation_history):
    # Get interaction details
    interaction = get_queue_item(interaction_id)
    
    # Prepare conversation summary
    summary = generate_conversation_summary(conversation_history)
    
    # Find suitable human agent
    human_agent = find_available_human_agent(
        required_specialization=detect_specialization_need(conversation_history),
        language=interaction.metadata.get('language', 'pt-br')
    )
    
    if human_agent:
        # Update interaction status
        update_queue_item_status(
            interaction_id=interaction_id,
            new_status=QueueStatus.ESCALATED,
            assigned_to=human_agent.id,
            escalation_reason=reason
        )
        
        # Notify customer
        send_escalation_notification(
            customer_id=interaction.customer_id,
            estimated_wait_time=calculate_wait_time(human_agent)
        )
        
        # Send to human agent with context
        send_to_human_agent(interaction, human_agent, summary)
        
        # Update metrics
        update_escalation_metrics(interaction, reason)
        
        return True, human_agent.id
    else:
        # No human available, keep in queue with escalation flag
        update_queue_item(
            interaction_id=interaction_id,
            updates={
                'needs_human': True,
                'escalation_reason': reason,
                'priority_score': min(100, interaction.priority_score + 10)  # Boost priority
            }
        )
        
        # Notify customer of delay
        send_wait_notification(
            customer_id=interaction.customer_id,
            reason="high_demand"
        )
        
        return False, None
```

### 4. Finalização

Processo de conclusão do atendimento:

```python
def complete_interaction(interaction_id, resolution_data):
    # Get interaction details
    interaction = get_queue_item(interaction_id)
    
    # Update status
    update_queue_item_status(
        interaction_id=interaction_id,
        new_status=QueueStatus.COMPLETED
    )
    
    # Store resolution data
    store_interaction_resolution(
        interaction_id=interaction_id,
        resolution_type=resolution_data['type'],
        resolution_details=resolution_data['details'],
        satisfaction_score=resolution_data.get('satisfaction_score'),
        agent_id=interaction.assigned_to
    )
    
    # Free up agent
    update_agent_status(
        agent_id=interaction.assigned_to,
        new_load=decrease_agent_load(interaction.assigned_to)
    )
    
    # Update metrics
    update_completion_metrics(interaction, resolution_data)
    
    # Archive interaction for historical analysis
    archive_interaction(interaction_id)
```

## Métricas e Monitoramento

### 1. Métricas da Fila

- **Volume de Interações**
  - Total de interações por período
  - Taxa de entrada (interações/minuto)
  - Picos e vales de tráfego

- **Tempos de Processamento**
  - Tempo médio de espera
  - Tempo médio de atendimento
  - Tempo total de resolução

- **Distribuição por Prioridade**
  - Percentual por nível de prioridade
  - Tempo de espera por nível

- **Escalonamento**
  - Taxa de escalonamento para humanos
  - Tempo médio até escalonamento
  - Distribuição de razões de escalonamento

### 2. Dashboards em Tempo Real

Painéis para monitoramento contínuo:

- **Visão Geral da Fila**
  - Status atual (tamanho, classificação por prioridade)
  - Gráfico de tendência (últimas 24h)
  - Alertas de capacidade

- **Desempenho dos Agentes**
  - Taxa de resolução
  - Tempo médio de resposta
  - Satisfação do cliente

- **Mapa de Calor Temporal**
  - Visualização de volume por hora/dia da semana
  - Previsão de demanda próximas horas

### 3. Sistema de Alertas

Gatilhos para notificação de operadores:

- **Capacidade da Fila**
  - Alerta quando fila excede 80% da capacidade
  - Alerta para tempo de espera acima do limiar

- **Anomalias**
  - Detecção de picos anormais de volume
  - Padrões incomuns de escalonamento

- **Falhas do Sistema**
  - Erros de processamento
  - Tempos de resposta anormais dos agentes

## Otimização Contínua

### 1. Análise Retrospectiva

- Identificação de padrões em escalonamentos
- Análise de conversas para melhorias no agente
- Ajuste de parâmetros de priorização

### 2. Ajustes Dinâmicos

- Atualização de regras de priorização baseadas em resultados
- Ajuste automático de pesos do algoritmo
- Recalibração periódica de limites de carga

### 3. Previsão de Demanda

- Modelos preditivos para volume de interações
- Alocação preventiva de recursos
- Gestão proativa de capacidade

## Integrações

### 1. CRM e Sistemas de Suporte

- Sincronização bidirecional com CRM
- Integração com sistema de tickets
- Histórico unificado de interações

### 2. Canais de Comunicação

- WhatsApp Business API
- Chat Web
- Aplicativo móvel
- SMS

### 3. Sistemas Internos

- ERP para informações de pedidos
- Sistema de logística para rastreamento
- Gestão de inventário

## Implementação Técnica

### 1. Tecnologias Recomendadas

- **Backend**:
  - Python (FastAPI ou Django) para lógica de fila
  - Redis para filas em memória e cache
  - PostgreSQL para armazenamento persistente

- **Processamento em Tempo Real**:
  - Kafka para streaming de eventos
  - Celery para processamento assíncrono

- **Monitoramento**:
  - Prometheus para métricas
  - Grafana para dashboards
  - ELK Stack para logs

### 2. Arquitetura Serverless

Para escalabilidade dinâmica, uma arquitetura serverless é recomendada:

- AWS Lambda ou Google Cloud Functions para processamento
- DynamoDB ou Firestore para armazenamento
- API Gateway para endpoints
- CloudWatch ou Stackdriver para monitoramento

### 3. Estratégia de Alta Disponibilidade

- Replicação multi-zona
- Cache distribuído
- Estratégia de fallback para indisponibilidade
- Recuperação automática de falhas

## Plano de Implementação

### Fase 1: MVP (1-2 meses)

- Sistema básico de fila FIFO com priorização simples
- Integração com WhatsApp API
- Escalonamento manual para humanos
- Métricas fundamentais

### Fase 2: Priorização Inteligente (2-3 meses)

- Algoritmo completo de priorização
- Sistema de distribuição de carga
- Escalonamento automático baseado em regras
- Dashboards em tempo real

### Fase 3: Otimização e Machine Learning (3-4 meses)

- Modelos preditivos para priorização
- Aprendizado contínuo baseado em resultados
- Automação avançada de escalonamento
- Previsão de demanda e alocação proativa

### Fase 4: Integração Avançada (4-6 meses)

- Conexão com múltiplos canais
- Sistema unificado de atendimento
- Inteligência contextual entre canais
- Análise avançada de desempenho

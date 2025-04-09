# Agente Autônomo de E-commerce para WhatsApp

Este projeto implementa um agente autônomo inteligente para vendas via WhatsApp, capaz de interagir com clientes, apresentar produtos, gerenciar carrinhos de compra e conduzir o processo de vendas utilizando técnicas avançadas de processamento de linguagem natural e aprendizado de máquina.

## Visão Geral

O agente autônomo conecta-se à API do WhatsApp Business para proporcionar uma experiência de compra completa e personalizada, desde a descoberta de produtos até a finalização do pedido. O sistema utiliza um modelo de linguagem avançado (LLM) customizado para o contexto de e-commerce, técnicas de persuasão éticas e uma arquitetura flexível que permite integração com plataformas de e-commerce existentes.

## Principais Funcionalidades

- **Integração com WhatsApp**: Comunicação bidirecional através da API oficial do WhatsApp Business
- **Processamento de Linguagem Natural**: Detecção de intenções, extração de entidades e análise de sentimento
- **Catálogo de Produtos**: Consulta de produtos, preços e disponibilidade em tempo real
- **Carrinho Virtual**: Gerenciamento completo de carrinho de compras via chat
- **Recomendações Personalizadas**: Sugestões baseadas em preferências e comportamento do usuário
- **Técnicas de Persuasão**: Implementação ética de princípios de neuromarketing e vendas consultivas
- **Sistema de Fila**: Gerenciamento inteligente de filas e priorização de atendimento
- **Análise e Métricas**: Rastreamento detalhado de conversões e desempenho de vendas

## Tecnologias Utilizadas

- **Backend**: Python 3.10+ com FastAPI
- **Banco de Dados**: PostgreSQL, MongoDB e Redis
- **Mensageria**: Kafka/RabbitMQ (para implementações em grande escala)
- **Machine Learning**: OpenAI API, LangChain
- **Infraestrutura**: Docker, Docker Compose

## Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- Conta de WhatsApp Business API
- Acesso a API de e-commerce (ou usar o mock interno para testes)
- Chave de API do OpenAI (ou outro provedor de LLM)

## Instalação e Execução

### Configuração do Ambiente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ecommerce-agente-autonomo.git
cd ecommerce-agente-autonomo
```

2. Configure o ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais e configurações
```

3. Inicie os serviços com Docker Compose:
```bash
docker-compose up -d
```

### Execução Local (Desenvolvimento)

1. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
uvicorn main:app --reload
```

## Arquitetura

O sistema está organizado em componentes modulares com responsabilidades bem definidas:

- **API Layer**: Gerencia endpoints e webhooks da API
- **Core Layer**: Contém a lógica central do agente autônomo
- **Services Layer**: Implementa integrações com serviços externos (WhatsApp, E-commerce)
- **NLP Layer**: Processa linguagem natural e gerencia o modelo LLM
- **Persuasion Layer**: Implementa técnicas de persuasão e vendas
- **Data Layer**: Gerencia persistência e acesso a dados

## Uso da API

### Webhook do WhatsApp

```
POST /api/webhook
```
Endpoint para receber mensagens do WhatsApp via webhook.

### Envio de Recomendações

```
POST /api/send-product-recommendations
```
Envia recomendações de produtos para um usuário específico.

### Gerenciamento de Carrinho

```
POST /api/cart/{action}
```
Gerencia operações no carrinho (add, remove, update, clear).

### Checkout

```
POST /api/checkout
```
Gera um checkout para o carrinho atual.

## Desenvolvimento

### Estrutura de Diretórios

```
ecommerce_agente_autonomo/
│
├── app/                       # Código principal da aplicação
│   ├── api/                   # Endpoints da API
│   ├── core/                  # Lógica central do agente
│   ├── models/                # Modelos de dados
│   ├── nlp/                   # Processamento de linguagem natural
│   ├── services/              # Serviços externos (WhatsApp, e-commerce)
│   ├── utils/                 # Utilitários diversos
│   ├── persuasion/            # Técnicas de persuasão e vendas
│   ├── database/              # Acesso a banco de dados
│   └── metrics/               # Sistema de métricas
│
├── docs/                      # Documentação detalhada
├── tests/                     # Testes automatizados
├── config/                    # Arquivos de configuração
├── scripts/                   # Scripts utilitários
```

### Padrões de Design

Este projeto segue os princípios SOLID:

- **S**: Single Responsibility Principle - Cada classe tem uma única responsabilidade
- **O**: Open/Closed Principle - Entidades abertas para extensão, fechadas para modificação
- **L**: Liskov Substitution Principle - Interfaces consistentes permitem substituição de implementações
- **I**: Interface Segregation Principle - Interfaces específicas para diferentes necessidades
- **D**: Dependency Inversion Principle - Dependências de abstrações, não de implementações concretas

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para dúvidas ou sugestões, entre em contato pelo email: seu.email@exemplo.com

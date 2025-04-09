# Sistema de Gamificação - Systentando ONE

Este documento detalha o sistema de gamificação implementado no ecossistema Systentando ONE, visando aumentar o engajamento, promover comportamentos positivos e criar uma comunidade colaborativa vibrante.

## Objetivos do Sistema de Gamificação

1. **Fomentar Contribuições**: Motivar desenvolvedores a contribuir ativamente
2. **Promover Qualidade**: Incentivar contribuições de alta qualidade
3. **Construir Comunidade**: Criar conexões entre desenvolvedores
4. **Reconhecer Expertise**: Destacar e valorizar conhecimentos especializados
5. **Equilibrar Recompensas**: Balancear incentivos intrínsecos e extrínsecos

## Elementos do Sistema

### Pontos e Experiência

- **Pontos de Contribuição (CP)**: Obtidos por atividades valiosas
- **Pontos de Experiência (XP)**: Acumulados ao longo do tempo, determinam o nível
- **Tokens de Equity (ET)**: Representam participação no sucesso do ecossistema

#### Fontes de Pontos

| Atividade | CP | XP | ET |
|-----------|-----|-----|-----|
| Commit aceito | 5-20 | 10 | 1-5 |
| Documentação | 10-30 | 15 | 2-8 |
| Revisão de código | 5-15 | 8 | 1-3 |
| Resposta em fórum | 2-10 | 5 | 0-1 |
| Resolução de desafio | 20-100 | 30 | 5-25 |
| Mentoria (hora) | 15 | 20 | 5 |
| Uso diário de produto | 1 | 2 | 0 |

### Níveis e Progressão

```
Nível 1: Iniciante (0-100 XP)
Nível 2: Aprendiz (101-300 XP)
Nível 3: Praticante (301-600 XP)
Nível 4: Especialista (601-1000 XP)
Nível 5: Mestre (1001-1500 XP)
Nível 6: Visionário (1501-2100 XP)
Nível 7: Pioneiro (2101-2800 XP)
Nível 8: Inovador (2801-3600 XP)
Nível 9: Virtuoso (3601-4500 XP)
Nível 10: Lenda (4501+ XP)
```

Cada nível desbloqueia:
- Novas funcionalidades na plataforma
- Capacidade de criar desafios mais complexos
- Maior peso em votos e revisões
- Acesso a eventos exclusivos

### Distintivos (Badges)

Os distintivos reconhecem conquistas específicas e habilidades demonstradas.

#### Categorias de Distintivos

1. **Técnicos**: Relacionados a habilidades e conhecimentos técnicos
   - Arquiteto de Soluções
   - Mestre do Frontend
   - Guru de Dados
   - Especialista em Segurança

2. **Comunidade**: Relacionados à participação e colaboração
   - Mentor Dedicado
   - Colaborador Frequente
   - Construtor de Pontes
   - Revisão Primorosa

3. **Desafios**: Relacionados à superação de desafios
   - Solucionador Bronze/Prata/Ouro
   - Primeiro Desafio
   - Maratonista (10+ desafios)
   - Velocista (solução rápida)

4. **Produtos**: Relacionados ao uso e contribuição em produtos específicos
   - Especialista ZEN
   - Guru Nutricional
   - Estrategista Financeiro
   - Empreendedor Digital

5. **Especiais**: Raros e difíceis de obter
   - Visionário (ideia que gerou produto de sucesso)
   - Pilar da Comunidade (contribuições transformadoras)
   - Lenda (reconhecimento excepcional)

### Desafios

Os desafios são missões com objetivos específicos e recompensas definidas.

#### Tipos de Desafios

1. **Técnicos**: Resolução de problemas de código
   - Otimização de algoritmos
   - Implementação de funcionalidades
   - Correção de bugs

2. **Negócios**: Criação de soluções para problemas reais
   - Modelagem de negócios
   - Validação de mercado
   - Estratégias de crescimento

3. **Design**: Criação de experiências de usuário
   - Interfaces intuitivas
   - Fluxos de usuário
   - Design visual

4. **Comunidade**: Atividades colaborativas
   - Organização de eventos
   - Mentorias
   - Documentação colaborativa

#### Estrutura de um Desafio

```typescript
interface Challenge {
  title: string;              // Título do desafio
  description: string;        // Descrição detalhada
  acceptance_criteria: string[]; // Critérios de aceitação
  difficulty: 'Easy' | 'Medium' | 'Hard' | 'Expert'; // Dificuldade
  time_estimate: string;      // Tempo estimado
  rewards: {                  // Recompensas
    cp: number;               // Pontos de contribuição
    xp: number;               // Pontos de experiência
    et: number;               // Tokens de equity
    badges?: string[];        // Distintivos possíveis
  };
  submission_type: 'Code' | 'Document' | 'Design' | 'Presentation'; // Tipo de submissão
  deadline?: Date;            // Prazo (opcional)
}
```

### Quadro de Líderes (Leaderboards)

Múltiplos quadros de líderes motivam diferentes tipos de contribuição:

1. **Global**: Classificação geral por total de pontos
2. **Mensal**: Atividade recente (últimos 30 dias)
3. **Por Categoria**: Específicos por tipo de contribuição
4. **Por Produto**: Líderes em cada produto do ecossistema

### Recompensas

#### Recompensas Intrínsecas
- Reconhecimento da comunidade
- Distintivos exclusivos
- Destaque no perfil
- Acesso antecipado a recursos

#### Recompensas Extrínsecas
- Tokens de equity (participação no sucesso)
- Acesso a eventos presenciais
- Oportunidades de mentoria de especialistas
- Recursos premium sem custo
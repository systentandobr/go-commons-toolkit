import logging
import random
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import openai

from app.services.interfaces import PersuasionServiceInterface
from app.utils.config import settings

logger = logging.getLogger(__name__)

class PersuasionEngine(PersuasionServiceInterface):
    """
    Motor de persuasão que aplica técnicas de vendas baseadas em princípios de psicologia
    comportamental e marketing para aumentar as taxas de conversão.
    """
    
    def __init__(self):
        """Inicializa o motor de persuasão e carrega as técnicas disponíveis."""
        # Configuração da API OpenAI
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        
        # Carrega as técnicas de persuasão e objections
        self._load_persuasion_techniques()
        self._load_objection_handlers()
        
        # Cache para armazenar eficácia das técnicas por usuário
        self._user_technique_effectiveness: Dict[str, Dict[str, float]] = {}
    
    def _load_persuasion_techniques(self):
        """Carrega as técnicas de persuasão disponíveis."""
        self.techniques = {
            # Princípios de Cialdini
            "reciprocity": {
                "description": "Oferecer valor antes de pedir algo em troca",
                "prompt": "Aplique o princípio da reciprocidade, oferecendo valor ou informação útil antes de sugerir uma compra.",
                "examples": [
                    "Aqui está um guia rápido sobre [benefício]. Aliás, temos produtos que podem ajudar ainda mais...",
                    "Vou compartilhar uma dica exclusiva sobre [tema]. Por falar nisso, nosso [produto] complementa isso perfeitamente..."
                ]
            },
            "social_proof": {
                "description": "Destacar popularidade e aprovação social",
                "prompt": "Utilize prova social mencionando popularidade, avaliações positivas ou escolhas comuns de outros clientes.",
                "examples": [
                    "Este é nosso produto mais vendido na categoria, com mais de 500 avaliações 5 estrelas!",
                    "Muitos clientes como você escolhem esta opção por causa da excelente relação custo-benefício."
                ]
            },
            "scarcity": {
                "description": "Enfatizar disponibilidade limitada ou tempo",
                "prompt": "Destaque escassez legítima, como estoque limitado ou ofertas por tempo determinado.",
                "examples": [
                    "Temos apenas 5 unidades disponíveis deste modelo. Na última reposição, esgotou em 2 dias.",
                    "Esta promoção é válida apenas até amanhã. Depois disso, o preço voltará ao normal."
                ]
            },
            "authority": {
                "description": "Usar autoridade e expertise",
                "prompt": "Invoque autoridade através de especialistas, pesquisas ou certificações relevantes.",
                "examples": [
                    "Segundo dermatologistas, este ingrediente é essencial para combater os sinais de envelhecimento.",
                    "Este produto recebeu certificação do Instituto de Qualidade, garantindo máxima eficiência."
                ]
            },
            "consistency": {
                "description": "Construir sobre compromissos anteriores",
                "prompt": "Explore consistência destacando escolhas anteriores do cliente ou valores expressos.",
                "examples": [
                    "Já que você valoriza produtos naturais, esta opção é perfeita pois é 100% orgânica.",
                    "Como você mencionou que durabilidade é importante, recomendo este modelo que tem 5 anos de garantia."
                ]
            },
            "liking": {
                "description": "Criar afinidade e identificação",
                "prompt": "Construa afinidade encontrando pontos em comum e demonstrando entendimento das necessidades.",
                "examples": [
                    "Entendo perfeitamente sua preocupação com qualidade. Eu também sempre priorizo isso nas minhas compras.",
                    "É ótimo encontrar alguém que aprecia design minimalista como você. Temos produtos alinhados com esse estilo."
                ]
            },
            
            # Modelo AIDA
            "attention": {
                "description": "Capturar atenção inicial",
                "prompt": "Capture a atenção com fatos surpreendentes, perguntas intrigantes ou estatísticas impactantes.",
                "examples": [
                    "Sabia que 87% das pessoas estão usando o produto errado para sua necessidade específica?",
                    "Imagine economizar 3 horas por semana em tarefas repetitivas. Nosso produto torna isso possível."
                ]
            },
            "interest": {
                "description": "Despertar interesse com benefícios",
                "prompt": "Aprofunde o interesse destacando benefícios específicos e relevantes para o cliente.",
                "examples": [
                    "Este modelo foi projetado especificamente para resolver o problema que você mencionou, através da tecnologia X.",
                    "Diferente de outras opções, nosso produto oferece três benefícios exclusivos: [lista]."
                ]
            },
            "desire": {
                "description": "Criar desejo pela experiência",
                "prompt": "Intensifique o desejo através de visualização, narrativas e conexão emocional.",
                "examples": [
                    "Imagine acordar todas as manhãs com a pele radiante e hidratada, sentindo-se confiante o dia todo.",
                    "Nossos clientes relatam uma sensação imediata de bem-estar logo na primeira aplicação."
                ]
            },
            "action": {
                "description": "Incentivar ação imediata",
                "prompt": "Promova ação com chamadas claras, remoção de obstáculos e senso de urgência legítimo.",
                "examples": [
                    "Posso adicionar ao seu carrinho agora? É super fácil finalizar depois.",
                    "Qual seria melhor para você: entrega expressa em 24h ou padrão com frete grátis?"
                ]
            },
            
            # Estratégias de neuromarketing
            "framing": {
                "description": "Enquadrar informações favoravelmente",
                "prompt": "Apresente informações de modo favorável, como preço diário vs. mensal ou ganhos vs. perdas.",
                "examples": [
                    "Por apenas R$3 por dia, menos que um café, você terá acesso completo a todos os benefícios.",
                    "Este investimento se paga em 2 meses, considerando a economia que proporcionará."
                ]
            },
            "anchoring": {
                "description": "Usar âncoras de referência",
                "prompt": "Estabeleça pontos de referência para influenciar a percepção de valor.",
                "examples": [
                    "Normalmente este modelo custa R$1.999, mas hoje está com 30% de desconto: R$1.399.",
                    "Comparado com alternativas premium que custam mais de R$5.000, nosso produto oferece qualidade similar por R$2.499."
                ]
            },
            "pain_reduction": {
                "description": "Reduzir a dor da compra",
                "prompt": "Minimize o desconforto da compra destacando parcelamento, garantias e retorno do investimento.",
                "examples": [
                    "Você pode parcelar em até 10x sem juros e testar por 30 dias com garantia de devolução.",
                    "Considerando a durabilidade de 5 anos, o custo diário é de apenas centavos."
                ]
            },
            "storytelling": {
                "description": "Usar narrativas envolventes",
                "prompt": "Utilize histórias para criar conexão emocional e memorabilidade.",
                "examples": [
                    "Um cliente como você estava cético inicialmente, mas após um mês de uso, nos enviou um depoimento emocionante...",
                    "A história por trás deste produto começou quando nosso fundador enfrentou o mesmo desafio que você..."
                ]
            }
        }
        
        logger.info(f"Loaded {len(self.techniques)} persuasion techniques")
    
    def _load_objection_handlers(self):
        """Carrega os tratamentos para objeções comuns."""
        self.objection_handlers = {
            "price": {
                "description": "Cliente considera o preço alto",
                "prompt": "Aborde objeções de preço mostrando valor, comparando alternativas e destacando ROI.",
                "examples": [
                    "Entendo sua preocupação com o investimento. Considerando a durabilidade de 5 anos, o custo diário é menor que R$1. Além disso, oferecemos parcelamento em até 10x sem juros.",
                    "Este modelo tem um custo inicial maior, mas a economia a longo prazo é significativa. Nossos clientes economizam em média 30% em energia comparado a modelos mais baratos."
                ]
            },
            "need": {
                "description": "Cliente não vê necessidade",
                "prompt": "Demonstre valor prático e resolução de problemas que o cliente pode não ter percebido.",
                "examples": [
                    "Muitos clientes não percebem quanto tempo perdem com esse problema até experimentarem a solução. Em média, nossos clientes economizam 5 horas por semana.",
                    "Entendo que pareça um luxo agora, mas considere os benefícios a longo prazo: menos manutenção, maior durabilidade e melhor experiência diária."
                ]
            },
            "urgency": {
                "description": "Cliente quer adiar decisão",
                "prompt": "Aborde adiamento destacando custos de oportunidade e benefícios imediatos.",
                "examples": [
                    "Compreendo a decisão de esperar, mas vale considerar que a promoção atual termina hoje. Além disso, você começaria a aproveitar os benefícios imediatamente.",
                    "Muitos clientes nos dizem que se arrependeram de não ter adquirido antes, pois poderiam ter economizado/aproveitado por mais tempo."
                ]
            },
            "competition": {
                "description": "Cliente menciona concorrentes",
                "prompt": "Reconheça a concorrência e destaque diferenciais exclusivos de forma respeitosa.",
                "examples": [
                    "Sim, conheço esse produto. É uma boa opção também. O que nos diferencia é [benefício exclusivo] e nosso suporte pós-venda premiado.",
                    "Entendo a comparação. Muitos clientes que migraram para nossa solução destacam três vantagens principais: [lista de diferenciais]."
                ]
            },
            "trust": {
                "description": "Cliente demonstra desconfiança",
                "prompt": "Construa confiança com garantias, transparência e provas concretas.",
                "examples": [
                    "Sua cautela é totalmente compreensível. Por isso oferecemos garantia de 90 dias sem questionamentos, e todas as nossas avaliações são verificadas por terceiros.",
                    "Entendo sua preocupação. Trabalhamos com [certificações de segurança] e nossos 15 anos no mercado refletem nosso compromisso com a satisfação do cliente."
                ]
            },
            "features": {
                "description": "Cliente questiona características",
                "prompt": "Explique características, conectando-as claramente aos benefícios e necessidades.",
                "examples": [
                    "Esta característica foi desenvolvida especificamente para resolver [problema], algo que nossos clientes frequentemente mencionavam.",
                    "Entendo que pareça complexo, mas na prática isso significa que você conseguirá [benefício concreto] com muito menos esforço."
                ]
            }
        }
        
        logger.info(f"Loaded {len(self.objection_handlers)} objection handlers")
    
    async def select_technique(self, user_id: str, product_id: Optional[str], context: Dict[str, Any]) -> str:
        """Seleciona a técnica de persuasão mais adequada para o contexto."""
        try:
            # Obtém o estágio atual da conversa
            stage = context.get("stage", "unknown")
            intent = context.get("intent", "unknown")
            sentiment = context.get("sentiment", 0.0)
            
            # Técnicas eficazes para este usuário (se houver histórico)
            effective_techniques = self._get_effective_techniques(user_id)
            
            # Seleciona as técnicas candidatas com base no estágio e intenção
            candidates = []
            
            # Estágio inicial (saudação, exploração)
            if stage in ["greeting", "exploring"]:
                candidates.extend(["attention", "reciprocity", "storytelling"])
                
                # Se o sentimento for positivo, pode usar liking
                if sentiment > 0.3:
                    candidates.append("liking")
            
            # Estágio de detalhes do produto
            elif stage == "product_details":
                candidates.extend(["interest", "social_proof", "authority", "desire"])
                
                # Se houver produto específico, pode usar escassez se legítima
                if product_id:
                    candidates.append("scarcity")
            
            # Estágio de carrinho ou checkout
            elif stage in ["cart_management", "checkout"]:
                candidates.extend(["action", "anchoring", "pain_reduction", "framing"])
                
                # Consistência é boa para quem já tem itens no carrinho
                if context.get("cart_item_count", 0) > 0:
                    candidates.append("consistency")
            
            # Considera as técnicas eficazes para este usuário
            if effective_techniques and random.random() < 0.7:  # 70% de chance de usar uma técnica eficaz anterior
                # Intersecção entre candidatas e eficazes, se existir
                effective_candidates = [t for t in candidates if t in effective_techniques]
                if effective_candidates:
                    return random.choice(effective_candidates)
            
            # Se chegou aqui, escolhe aleatoriamente entre as candidatas
            if candidates:
                return random.choice(candidates)
            
            # Fallback para uma técnica genérica
            return random.choice(["interest", "social_proof", "reciprocity"])
            
        except Exception as e:
            logger.error(f"Error selecting persuasion technique: {e}")
            return "interest"  # Fallback seguro
    
    async def apply_technique(self, technique: str, message: str, context: Dict[str, Any]) -> str:
        """Aplica uma técnica de persuasão a uma mensagem."""
        try:
            # Verifica se a técnica existe
            if technique not in self.techniques:
                logger.warning(f"Unknown persuasion technique: {technique}")
                return message
            
            # Obtém os detalhes da técnica
            technique_info = self.techniques[technique]
            
            # Prepara o contexto para o prompt
            context_str = "\n".join([f"{key}: {value}" for key, value in context.items() if key != "user_id"])
            
            # Exemplos para few-shot learning
            examples_str = "\n".join([f"- {ex}" for ex in technique_info["examples"]])
            
            # Prompt para o LLM
            prompt = f"""
            Você é um especialista em persuasão e vendas para e-commerce.
            
            MENSAGEM ORIGINAL:
            "{message}"
            
            CONTEXTO:
            {context_str}
            
            TÉCNICA DE PERSUASÃO: {technique} - {technique_info["description"]}
            
            INSTRUÇÕES:
            {technique_info["prompt"]}
            
            EXEMPLOS DA TÉCNICA:
            {examples_str}
            
            Reescreva a mensagem original aplicando a técnica de persuasão especificada, mantendo o conteúdo principal e o tom adequado para uma conversa de WhatsApp. A resposta deve ser natural e não parecer manipulativa ou excessivamente comercial. Mantenha um tom amigável e autêntico.
            
            REGRAS IMPORTANTES:
            1. Mantenha a mensagem concisa e direta.
            2. Não mencione explicitamente que está usando uma técnica de persuasão.
            3. Mantenha a essência e informações importantes da mensagem original.
            4. Aplique a técnica de forma sutil e natural.
            5. Preserve o contexto e propósito da mensagem original.
            
            MENSAGEM REESCRITA:
            """
            
            # Chamada para o LLM
            completion = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em persuasão ética para e-commerce."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            # Extraindo a resposta
            persuasive_message = completion.choices[0].message.content.strip()
            
            # Removendo prefixos que o modelo possa adicionar
            if persuasive_message.startswith("MENSAGEM REESCRITA:"):
                persuasive_message = persuasive_message[len("MENSAGEM REESCRITA:"):].strip()
            
            logger.info(f"Applied persuasion technique: {technique}")
            return persuasive_message
            
        except Exception as e:
            logger.error(f"Error applying persuasion technique: {e}")
            return message  # Retorna a mensagem original em caso de erro
    
    async def handle_objection(self, objection_type: str, product_id: str) -> str:
        """Gera uma resposta para lidar com uma objeção específica."""
        try:
            # Verifica se o tipo de objeção é conhecido
            if objection_type not in self.objection_handlers:
                logger.warning(f"Unknown objection type: {objection_type}")
                return "Entendo sua preocupação. Vamos analisar melhor essa questão para encontrar a melhor solução para você."
            
            # Obtém os detalhes do handler
            handler_info = self.objection_handlers[objection_type]
            
            # Seleciona uma resposta de exemplo
            if handler_info["examples"]:
                response = random.choice(handler_info["examples"])
                logger.info(f"Selected objection handler: {objection_type}")
                return response
            
            # Fallback
            return "Entendo sua preocupação. Vamos trabalhar juntos para encontrar a melhor solução para você."
            
        except Exception as e:
            logger.error(f"Error handling objection: {e}")
            return "Entendo sua preocupação. Gostaria de oferecer mais informações para ajudar em sua decisão."
    
    async def track_effectiveness(self, technique: str, user_id: str, result: bool) -> None:
        """Registra a eficácia de uma técnica para um usuário."""
        try:
            # Inicializa o dicionário para o usuário se não existir
            if user_id not in self._user_technique_effectiveness:
                self._user_technique_effectiveness[user_id] = {}
            
            # Obtém o histórico atual
            user_techniques = self._user_technique_effectiveness[user_id]
            
            # Atualiza a eficácia da técnica (média móvel)
            if technique in user_techniques:
                # Peso maior para o resultado mais recente (70/30)
                current_score = user_techniques[technique]
                user_techniques[technique] = 0.3 * current_score + 0.7 * (1.0 if result else 0.0)
            else:
                # Primeira ocorrência
                user_techniques[technique] = 1.0 if result else 0.0
            
            logger.info(f"Updated effectiveness for technique {technique} for user {user_id}: {user_techniques[technique]:.2f}")
            
            # Em uma implementação real, salvaríamos isso em um banco de dados
            
        except Exception as e:
            logger.error(f"Error tracking technique effectiveness: {e}")
    
    def _get_effective_techniques(self, user_id: str) -> List[str]:
        """Retorna as técnicas mais eficazes para um usuário específico."""
        try:
            if user_id not in self._user_technique_effectiveness:
                return []
            
            user_techniques = self._user_technique_effectiveness[user_id]
            
            # Considera eficazes as técnicas com score > 0.5
            effective_techniques = [
                technique for technique, score in user_techniques.items()
                if score > 0.5
            ]
            
            return effective_techniques
            
        except Exception as e:
            logger.error(f"Error getting effective techniques: {e}")
            return []

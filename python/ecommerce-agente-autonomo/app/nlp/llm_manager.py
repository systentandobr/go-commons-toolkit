import logging
import json
import openai
import tiktoken
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from app.utils.config import settings
from app.services.interfaces import NLPServiceInterface

logger = logging.getLogger(__name__)

class LLMManager(NLPServiceInterface):
    """Gerenciador do modelo de linguagem para processamento de texto e geração de respostas."""
    
    def __init__(self):
        """Inicializa o gerenciador LLM configurando a API e carregando recursos necessários."""
        # Configuração da API OpenAI
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        
        # Tokenizador para controle de contexto
        self.tokenizer = tiktoken.encoding_for_model(self.model)
        
        # Cache em memória para contextos de sessão (em um sistema real, seria Redis)
        self._session_contexts: Dict[str, List[Dict[str, Any]]] = {}
        
        # Carrega os modelos de intenção e as entidades suportadas
        self._load_intent_models()
        self._load_entity_extractors()
    
    def _load_intent_models(self):
        """Carrega os modelos de classificação de intenção."""
        # Em uma implementação real, aqui carregaríamos modelos específicos
        # para classificação de intenção. Por simplicidade, usaremos o LLM.
        logger.info("Intent models initialized")
    
    def _load_entity_extractors(self):
        """Carrega os extratores de entidades."""
        # Em uma implementação real, carregaríamos modelos de NER ou 
        # outras ferramentas de extração. Por simplicidade, usaremos o LLM.
        logger.info("Entity extractors initialized")
    
    async def detect_intent(self, text: str, session_id: str, language_code: str = "pt-br") -> Dict[str, Any]:
        """Detecta a intenção em um texto."""
        if not text:
            return {"intent": "unknown", "confidence": 0.0}
        
        # Define um conjunto básico de intenções para e-commerce
        intents = [
            "greeting",  # Saudação inicial
            "search_product",  # Busca por um produto
            "browse_category",  # Navegação por categoria
            "product_info",  # Informações sobre produto específico
            "add_to_cart",  # Adicionar ao carrinho
            "view_cart",  # Ver o carrinho atual
            "remove_from_cart",  # Remover do carrinho
            "checkout",  # Finalizar compra
            "payment",  # Informações sobre pagamento
            "shipping",  # Informações sobre envio
            "order_status",  # Status do pedido
            "support",  # Suporte ao cliente
            "complaint",  # Reclamação
            "farewell",  # Despedida
        ]
        
        try:
            # Contexto para o prompt
            prompt = f"""
            Analise o texto a seguir e determine a intenção do usuário.
            A intenção deve ser uma das seguintes:
            {', '.join(intents)}
            
            Texto: "{text}"
            
            Considere o contexto de um chat de e-commerce, onde o usuário está interagindo com um agente de vendas.
            Retorne apenas o nome da intenção e a probabilidade (entre 0.0 e 1.0) no formato JSON:
            {{"intent": "nome_da_intencao", "confidence": 0.95}}
            """
            
            completion = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em classificação de intenções para e-commerce."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Baixa temperatura para respostas mais determinísticas
                max_tokens=100,
                n=1
            )
            
            response_text = completion.choices[0].message.content.strip()
            # Extrair apenas o JSON da resposta
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                intent_data = json.loads(response_text)
                # Validação básica
                if "intent" not in intent_data or "confidence" not in intent_data:
                    raise ValueError("Missing required fields in response")
                
                logger.info(f"Detected intent: {intent_data['intent']} with confidence {intent_data['confidence']}")
                return intent_data
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse intent JSON: {response_text}")
                return {"intent": "unknown", "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return {"intent": "unknown", "confidence": 0.0}
    
    async def extract_entities(self, text: str, session_id: str) -> List[Dict[str, Any]]:
        """Extrai entidades de um texto."""
        if not text:
            return []
        
        # Define as entidades relevantes para e-commerce
        entity_types = [
            "product",  # Nome ou ID de produto
            "category",  # Categoria de produto
            "brand",  # Marca
            "price",  # Preço ou faixa de preço
            "quantity",  # Quantidade
            "color",  # Cor
            "size",  # Tamanho
            "payment_method",  # Método de pagamento
            "location",  # Localização/endereço
            "date",  # Data
            "search_query",  # Termos de busca
            "feature",  # Característica de produto
        ]
        
        try:
            # Contexto para o prompt
            prompt = f"""
            Analise o texto a seguir e extraia todas as entidades relevantes.
            As entidades podem ser dos seguintes tipos:
            {', '.join(entity_types)}
            
            Texto: "{text}"
            
            Considere o contexto de um chat de e-commerce.
            Retorne as entidades no formato JSON como uma lista de objetos, cada um com os campos:
            - type: o tipo da entidade
            - value: o valor extraído
            - confidence: confiança da extração (entre 0.0 e 1.0)
            
            Exemplo:
            [
                {{"type": "product", "value": "iPhone 13", "confidence": 0.95}},
                {{"type": "color", "value": "preto", "confidence": 0.8}}
            ]
            
            Se não encontrar nenhuma entidade, retorne uma lista vazia: []
            """
            
            completion = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em extração de entidades para e-commerce."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Baixa temperatura para respostas mais determinísticas
                max_tokens=300,
                n=1
            )
            
            response_text = completion.choices[0].message.content.strip()
            # Extrair apenas o JSON da resposta
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                entities = json.loads(response_text)
                if not isinstance(entities, list):
                    raise ValueError("Response is not a list")
                
                # Validação básica
                for entity in entities:
                    if "type" not in entity or "value" not in entity or "confidence" not in entity:
                        raise ValueError(f"Missing required fields in entity: {entity}")
                
                logger.info(f"Extracted {len(entities)} entities from text")
                return entities
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse entities JSON: {response_text}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analisa o sentimento de um texto."""
        if not text:
            return {"score": 0.0, "magnitude": 0.0, "label": "neutral"}
        
        try:
            # Contexto para o prompt
            prompt = f"""
            Analise o sentimento do seguinte texto:
            
            "{text}"
            
            Considere o contexto de um chat de e-commerce, onde um cliente está interagindo com um agente de vendas.
            Retorne apenas o resultado no formato JSON:
            {{
                "score": valor entre -1.0 (muito negativo) e 1.0 (muito positivo),
                "magnitude": valor entre 0.0 e 1.0 representando a intensidade do sentimento,
                "label": "positivo", "negativo", ou "neutro"
            }}
            """
            
            completion = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de sentimento."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Baixa temperatura para respostas mais determinísticas
                max_tokens=100,
                n=1
            )
            
            response_text = completion.choices[0].message.content.strip()
            # Extrair apenas o JSON da resposta
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                sentiment_data = json.loads(response_text)
                # Validação básica
                if "score" not in sentiment_data or "magnitude" not in sentiment_data or "label" not in sentiment_data:
                    raise ValueError("Missing required fields in response")
                
                logger.info(f"Sentiment analysis: {sentiment_data['label']} (score: {sentiment_data['score']})")
                return sentiment_data
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse sentiment JSON: {response_text}")
                return {"score": 0.0, "magnitude": 0.0, "label": "neutral"}
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"score": 0.0, "magnitude": 0.0, "label": "neutral"}
    
    async def generate_response(self, intent: str, entities: List[Dict[str, Any]], 
                               context: Dict[str, Any], language_code: str = "pt-br") -> str:
        """Gera uma resposta baseada na intenção, entidades e contexto."""
        try:
            # Prepara o contexto da conversa
            session_id = context.get("session_id", "default")
            conversation_history = self._get_conversation_history(session_id)
            
            # Formata o contexto para o prompt
            context_str = "\n".join([f"- {key}: {value}" for key, value in context.items()])
            entities_str = "\n".join([f"- {entity['type']}: {entity['value']}" for entity in entities])
            
            # Prepara instruções específicas para cada intenção
            instructions = self._get_intent_instructions(intent)
            
            # Contexto para o prompt
            system_prompt = f"""
            Você é um agente de vendas de e-commerce especializado em atendimento ao cliente via WhatsApp.
            Você deve responder de maneira conversacional, amigável e profissional.
            
            REGRAS IMPORTANTES:
            1. Mantenha as respostas concisas e diretas, no estilo de mensagens de WhatsApp.
            2. Use um tom amigável, mas profissional.
            3. Sempre ajude o cliente a encontrar produtos e realizar compras.
            4. Use técnicas de vendas sutis e éticas para aumentar conversões.
            5. Não invente informações sobre produtos específicos.
            6. Quando não souber alguma informação, seja honesto e ofereça alternativas.
            7. Use emojis com moderação para tornar a conversa mais agradável.
            
            INTENÇÃO DETECTADA DO USUÁRIO: {intent}
            
            ENTIDADES IDENTIFICADAS:
            {entities_str if entities else "Nenhuma entidade identificada."}
            
            CONTEXTO DA CONVERSA:
            {context_str}
            
            INSTRUÇÕES ESPECÍFICAS:
            {instructions}
            """
            
            # Constrói o histórico de mensagens para o LLM
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Adiciona o histórico recente da conversa, se disponível
            for msg in conversation_history[-5:]:  # Limita a 5 mensagens anteriores
                messages.append(msg)
            
            # Adiciona a instrução para gerar a resposta
            messages.append({
                "role": "user", 
                "content": "Gere uma resposta apropriada para o usuário com base na intenção, entidades e contexto fornecidos."
            })
            
            # Gera a resposta
            completion = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                n=1
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            # Atualiza o histórico da conversa
            self._update_conversation_history(session_id, "assistant", response_text)
            
            return response_text
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Desculpe, estou com dificuldades para processar sua solicitação no momento. Poderia tentar novamente?"
    
    def _get_intent_instructions(self, intent: str) -> str:
        """Retorna instruções específicas para cada tipo de intenção."""
        instructions = {
            "greeting": """
                Se for a primeira mensagem, dê boas-vindas calorosas ao cliente.
                Apresente-se como assistente virtual da loja.
                Ofereça ajuda para encontrar produtos ou responder dúvidas.
                Sugira algumas categorias populares para explorar.
            """,
            
            "search_product": """
                Confirme que entendeu o que o cliente está procurando.
                Se as entidades forem específicas o suficiente, sugira mostrar alguns produtos.
                Se for muito genérico, peça mais detalhes como categoria, marca ou características.
                Use perguntas abertas para entender melhor as necessidades do cliente.
            """,
            
            "browse_category": """
                Confirme a categoria que o cliente deseja explorar.
                Sugira subcategorias ou filtragens populares para refinar a busca.
                Mencione produtos populares ou promoções nessa categoria.
                Pergunte se o cliente tem preferências específicas dentro da categoria.
            """,
            
            "product_info": """
                Confirme o produto sobre o qual o cliente está perguntando.
                Forneça informações relevantes como características, preço e disponibilidade.
                Destaque benefícios e diferenciais do produto.
                Sugira informar sobre condições de pagamento e entrega.
                Pergunte se o cliente deseja adicionar o produto ao carrinho.
            """,
            
            "add_to_cart": """
                Confirme a adição do produto ao carrinho.
                Informe a quantidade e valor total atualizado do carrinho.
                Sugira produtos complementares (cross-sell).
                Pergunte se o cliente deseja continuar comprando ou finalizar o pedido.
            """,
            
            "view_cart": """
                Confirme os itens no carrinho, quantidade e valor total.
                Sugira finalizar a compra se o carrinho estiver completo.
                Sugira produtos relacionados se apropriado.
                Informe sobre políticas de desconto ou frete grátis, se aplicável.
            """,
            
            "remove_from_cart": """
                Confirme a remoção do item do carrinho.
                Atualize sobre o status atual do carrinho.
                Pergunte se o cliente gostaria de substituir por outro produto.
                Sugira alternativas ou pergunte sobre o motivo da remoção para melhor atendimento.
            """,
            
            "checkout": """
                Guie o cliente pelo processo de checkout.
                Confirme dados para entrega e pagamento.
                Explique claramente os próximos passos.
                Forneça informações sobre métodos de pagamento disponíveis.
                Esclareça dúvidas sobre segurança e garantias.
            """,
            
            "payment": """
                Forneça informações sobre métodos de pagamento disponíveis.
                Explique vantagens de cada método (parcelamento, descontos, etc.).
                Responda dúvidas sobre segurança e processamento.
                Ofereça assistência para concluir o pagamento.
            """,
            
            "shipping": """
                Forneça informações claras sobre prazos e custos de entrega.
                Explique as opções de envio disponíveis.
                Se possível, dê estimativas de tempo baseadas no CEP do cliente.
                Esclareça políticas de rastreamento e garantias de entrega.
            """,
            
            "order_status": """
                Confirme o pedido sobre o qual o cliente está perguntando.
                Forneça informações atualizadas sobre o status do pedido.
                Explique próximos passos e prazos esperados.
                Ofereça assistência em caso de dúvidas ou problemas.
            """,
            
            "support": """
                Identifique claramente a questão ou problema do cliente.
                Forneça informações e soluções diretas quando possível.
                Demonstre empatia e disposição para resolver o problema.
                Ofereça escalar para atendimento humano se necessário.
                Acompanhe até a resolução completa.
            """,
            
            "complaint": """
                Demonstre empatia e compreensão com a insatisfação do cliente.
                Peça desculpas pelo inconveniente.
                Busque entender completamente o problema antes de oferecer soluções.
                Proponha alternativas concretas para resolver a situação.
                Assegure que medidas serão tomadas para evitar problemas futuros.
            """,
            
            "farewell": """
                Agradeça ao cliente pelo contato.
                Reforce que estará disponível para qualquer dúvida futura.
                Convide o cliente a voltar em breve.
                Encerre de maneira amigável e profissional.
            """,
            
            "unknown": """
                Tente identificar a necessidade do cliente mesmo sem uma intenção clara.
                Faça perguntas abertas para entender melhor o que o cliente precisa.
                Sugira categorias populares ou promoções atuais para engajar o cliente.
                Ofereça assistência mais específica se necessário.
            """
        }
        
        return instructions.get(intent, instructions["unknown"])
    
    def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Obtém o histórico de conversa para uma sessão."""
        if session_id not in self._session_contexts:
            self._session_contexts[session_id] = []
        
        return self._session_contexts[session_id]
    
    def _update_conversation_history(self, session_id: str, role: str, content: str) -> None:
        """Atualiza o histórico de conversa para uma sessão."""
        if session_id not in self._session_contexts:
            self._session_contexts[session_id] = []
        
        # Adiciona a nova mensagem
        self._session_contexts[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limita o tamanho do histórico (em uma implementação real, usaríamos tokenização)
        if len(self._session_contexts[session_id]) > 20:
            self._session_contexts[session_id] = self._session_contexts[session_id][-20:]

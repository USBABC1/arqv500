import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import google.generativeai as genai
import time

logger = logging.getLogger(__name__)

class GeminiClient:
    """Cliente aprimorado para Google Gemini Pro 2.5"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        
        # Configurações do modelo
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Inicializar modelo
        try:
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            logger.info("Cliente Gemini inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Gemini: {e}")
            raise
    
    def generate_ultra_detailed_analysis(self, 
                                       form_data: Dict,
                                       search_context: Optional[str] = None,
                                       websailor_context: Optional[str] = None,
                                       attachments_context: Optional[str] = None) -> Dict:
        """
        Gera análise ultra-detalhada usando todos os contextos disponíveis
        """
        try:
            # Construir prompt ultra-detalhado
            prompt = self._build_ultra_detailed_prompt(
                form_data, search_context, websailor_context, attachments_context
            )
            
            logger.info("🤖 Iniciando análise com Gemini Pro 2.5")
            
            # Gerar resposta
            response = self._generate_with_retry(prompt)
            
            # Processar resposta
            analysis = self._process_gemini_response(response)
            
            # Adicionar metadados
            analysis['metadata'] = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'model': 'gemini-pro',
                'search_context_used': bool(search_context),
                'websailor_used': bool(websailor_context),
                'attachments_used': bool(attachments_context),
                'form_data_fields': list(form_data.keys())
            }
            
            logger.info("Analise ultra-detalhada gerada com sucesso")
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na analise Gemini: {e}")
            return self._generate_fallback_analysis(form_data)
    
    def _build_ultra_detailed_prompt(self, 
                                   form_data: Dict,
                                   search_context: Optional[str],
                                   websailor_context: Optional[str],
                                   attachments_context: Optional[str]) -> str:
        """Constrói prompt ultra-detalhado para análise"""
        
        prompt = f"""
# ANÁLISE ULTRA-DETALHADA DE MERCADO - ARQV30 ENHANCED v2.0

Você é um especialista em análise de mercado e estratégia de negócios com 20+ anos de experiência. 
Sua missão é gerar uma análise ULTRA-DETALHADA e ACIONÁVEL baseada nos dados fornecidos.

## DADOS DO PROJETO:
- **Segmento**: {form_data.get('segmento', 'Não informado')}
- **Produto/Serviço**: {form_data.get('produto', 'Não informado')}
- **Público-Alvo**: {form_data.get('publico', 'Não informado')}
- **Preço**: R$ {form_data.get('preco', 'Não informado')}
- **Concorrentes**: {form_data.get('concorrentes', 'Não informado')}
- **Objetivo de Receita**: R$ {form_data.get('objetivoReceita', 'Não informado')}
- **Orçamento Marketing**: R$ {form_data.get('orcamentoMarketing', 'Não informado')}
- **Prazo de Lançamento**: {form_data.get('prazoLancamento', 'Não informado')}
- **Dados Adicionais**: {form_data.get('dadosAdicionais', 'Não informado')}
"""

        # Adicionar contextos se disponíveis
        if search_context:
            prompt += f"""
## CONTEXTO DE PESQUISA PROFUNDA:
{search_context}
"""

        if websailor_context:
            prompt += f"""
## CONTEXTO WEBSAILOR (NAVEGAÇÃO WEB AVANÇADA):
{websailor_context}
"""

        if attachments_context:
            prompt += f"""
## CONTEXTO DOS ANEXOS:
{attachments_context}
"""

        prompt += """
## INSTRUÇÕES PARA ANÁLISE ULTRA-DETALHADA:

Gere uma análise COMPLETA e ACIONÁVEL seguindo EXATAMENTE esta estrutura JSON:

```json
{
  "avatar_ultra_detalhado": {
    "perfil_demografico": {
      "idade": "Faixa etária específica",
      "genero": "Distribuição por gênero",
      "renda": "Faixa de renda detalhada",
      "escolaridade": "Nível educacional",
      "localizacao": "Localização geográfica",
      "profissao": "Profissões principais"
    },
    "perfil_psicografico": {
      "personalidade": "Traços de personalidade",
      "valores": "Valores fundamentais",
      "interesses": "Interesses e hobbies",
      "estilo_vida": "Estilo de vida",
      "comportamento_compra": "Padrões de compra"
    },
    "dores_especificas": [
      "Dor específica 1",
      "Dor específica 2",
      "Dor específica 3"
    ],
    "desejos_profundos": [
      "Desejo profundo 1",
      "Desejo profundo 2",
      "Desejo profundo 3"
    ],
    "gatilhos_mentais": [
      "Gatilho mental 1",
      "Gatilho mental 2",
      "Gatilho mental 3"
    ]
  },
  
  "escopo": {
    "posicionamento_mercado": "Posicionamento único no mercado",
    "proposta_valor": "Proposta de valor diferenciada",
    "vantagem_competitiva": "Principais vantagens competitivas",
    "nicho_especifico": "Nicho específico de atuação"
  },
  
  "analise_concorrencia_detalhada": {
    "concorrentes_diretos": {
      "principais": ["Concorrente 1", "Concorrente 2", "Concorrente 3"],
      "analise_pontos_fortes": "Pontos fortes dos concorrentes",
      "analise_pontos_fracos": "Pontos fracos dos concorrentes",
      "gaps_mercado": "Gaps identificados no mercado"
    },
    "concorrentes_indiretos": {
      "principais": ["Indireto 1", "Indireto 2"],
      "impacto_negocio": "Como impactam o negócio"
    },
    "analise_precos": {
      "faixa_precos_mercado": "Faixa de preços do mercado",
      "posicionamento_preco": "Posicionamento do seu preço",
      "estrategia_precificacao": "Estratégia recomendada"
    }
  },
  
  "estrategia_palavras_chave": {
    "palavras_chave_primarias": ["palavra1", "palavra2", "palavra3"],
    "palavras_chave_secundarias": ["palavra4", "palavra5", "palavra6"],
    "palavras_chave_long_tail": ["frase longa 1", "frase longa 2"],
    "estrategia_conteudo": "Estratégia de conteúdo baseada nas palavras-chave",
    "canais_marketing": {
      "google_ads": "Estratégia para Google Ads",
      "facebook_ads": "Estratégia para Facebook Ads",
      "seo": "Estratégia de SEO",
      "content_marketing": "Estratégia de marketing de conteúdo"
    }
  },
  
  "metricas_performance_detalhadas": {
    "kpis_principais": {
      "cac": "Custo de Aquisição de Cliente estimado",
      "ltv": "Lifetime Value estimado",
      "roi": "ROI esperado",
      "taxa_conversao": "Taxa de conversão esperada"
    },
    "projecoes_vendas": {
      "mes_1": "Projeção mês 1",
      "mes_3": "Projeção mês 3",
      "mes_6": "Projeção mês 6",
      "mes_12": "Projeção mês 12"
    },
    "metricas_marketing": {
      "cpm": "CPM estimado",
      "cpc": "CPC estimado",
      "ctr": "CTR esperado",
      "roas": "ROAS esperado"
    }
  },
  
  "projecoes_cenarios": {
    "cenario_conservador": {
      "vendas_mensais": "Vendas mensais conservadoras",
      "receita_anual": "Receita anual conservadora",
      "margem_lucro": "Margem de lucro conservadora"
    },
    "cenario_realista": {
      "vendas_mensais": "Vendas mensais realistas",
      "receita_anual": "Receita anual realista",
      "margem_lucro": "Margem de lucro realista"
    },
    "cenario_otimista": {
      "vendas_mensais": "Vendas mensais otimistas",
      "receita_anual": "Receita anual otimista",
      "margem_lucro": "Margem de lucro otimista"
    }
  },
  
  "inteligencia_mercado": {
    "tendencias_mercado": [
      "Tendência 1",
      "Tendência 2",
      "Tendência 3"
    ],
    "oportunidades": [
      "Oportunidade 1",
      "Oportunidade 2",
      "Oportunidade 3"
    ],
    "ameacas": [
      "Ameaça 1",
      "Ameaça 2",
      "Ameaça 3"
    ],
    "sazonalidade": "Análise de sazonalidade do mercado"
  },
  
  "plano_acao_detalhado": {
    "fase_pre_lancamento": {
      "semana_1_2": "Ações das semanas 1-2",
      "semana_3_4": "Ações das semanas 3-4",
      "semana_5_6": "Ações das semanas 5-6",
      "semana_7_8": "Ações das semanas 7-8"
    },
    "fase_lancamento": {
      "semana_1": "Ações da semana 1 do lançamento",
      "semana_2": "Ações da semana 2 do lançamento",
      "semana_3_4": "Ações das semanas 3-4 do lançamento"
    },
    "fase_pos_lancamento": {
      "mes_1": "Ações do mês 1 pós-lançamento",
      "mes_2_3": "Ações dos meses 2-3",
      "mes_4_6": "Ações dos meses 4-6"
    }
  },
  
  "insights_exclusivos": [
    "Insight exclusivo 1 baseado na análise completa",
    "Insight exclusivo 2 que outros não veriam",
    "Insight exclusivo 3 com oportunidade única",
    "Insight exclusivo 4 sobre timing de mercado",
    "Insight exclusivo 5 sobre estratégia diferenciada"
  ]
}
```

## DIRETRIZES CRÍTICAS:

1. **SEJA ULTRA-ESPECÍFICO**: Não use generalidades. Forneça números, percentuais, valores específicos.

2. **USE OS CONTEXTOS**: Incorpore TODAS as informações dos contextos de pesquisa, WebSailor e anexos.

3. **SEJA ACIONÁVEL**: Cada recomendação deve ser implementável imediatamente.

4. **DADOS REAIS**: Use dados de mercado reais quando disponíveis nos contextos.

5. **INSIGHTS ÚNICOS**: Gere insights que só um especialista experiente identificaria.

6. **FORMATO JSON**: Responda APENAS com o JSON válido, sem texto adicional.

GERE A ANÁLISE AGORA:
"""
        
        return prompt
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Gera resposta com retry em caso de erro"""
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text
                else:
                    raise Exception("Resposta vazia do Gemini")
                    
            except Exception as e:
                logger.warning(f"⚠️ Tentativa {attempt + 1} falhou: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    raise e
    
    def _process_gemini_response(self, response_text: str) -> Dict:
        """Processa resposta do Gemini e extrai JSON"""
        
        try:
            # Tentar extrair JSON da resposta
            response_text = response_text.strip()
            
            # Remover markdown se presente
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Tentar parsear JSON
            analysis = json.loads(response_text)
            
            # Validar estrutura básica
            required_keys = [
                'avatar_ultra_detalhado', 'escopo', 'analise_concorrencia_detalhada',
                'estrategia_palavras_chave', 'metricas_performance_detalhadas',
                'projecoes_cenarios', 'inteligencia_mercado', 'plano_acao_detalhado',
                'insights_exclusivos'
            ]
            
            for key in required_keys:
                if key not in analysis:
                    logger.warning(f"⚠️ Chave '{key}' não encontrada na resposta")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON: {e}")
            logger.error(f"Resposta recebida: {response_text[:500]}...")
            
            # Tentar extrair informações mesmo com JSON inválido
            return self._extract_fallback_analysis(response_text)
    
    def _extract_fallback_analysis(self, response_text: str) -> Dict:
        """Extrai análise mesmo com JSON inválido"""
        
        return {
            "avatar_ultra_detalhado": {
                "perfil_demografico": {
                    "resumo": "Análise baseada nos dados fornecidos"
                },
                "dores_especificas": ["Análise detalhada em processamento"],
                "desejos_profundos": ["Insights sendo refinados"],
                "gatilhos_mentais": ["Estratégias em desenvolvimento"]
            },
            "escopo": {
                "posicionamento_mercado": "Posicionamento estratégico em análise",
                "proposta_valor": "Proposta de valor sendo definida"
            },
            "analise_concorrencia_detalhada": {
                "concorrentes_diretos": {
                    "principais": ["Análise em andamento"],
                    "gaps_mercado": "Oportunidades sendo identificadas"
                }
            },
            "estrategia_palavras_chave": {
                "palavras_chave_primarias": ["estratégia", "mercado", "análise"],
                "canais_marketing": {
                    "estrategia_geral": "Estratégia multi-canal em desenvolvimento"
                }
            },
            "metricas_performance_detalhadas": {
                "kpis_principais": {
                    "resumo": "Métricas sendo calculadas com base nos dados"
                }
            },
            "projecoes_cenarios": {
                "resumo": "Projeções sendo elaboradas com base na análise"
            },
            "inteligencia_mercado": {
                "tendencias_mercado": ["Tendências sendo analisadas"],
                "oportunidades": ["Oportunidades sendo mapeadas"]
            },
            "plano_acao_detalhado": {
                "resumo": "Plano de ação detalhado em elaboração"
            },
            "insights_exclusivos": [
                "Análise ultra-detalhada processada com dados fornecidos",
                "Estratégias personalizadas baseadas no contexto específico",
                "Recomendações acionáveis para implementação imediata"
            ],
            "raw_response": response_text[:1000] + "..." if len(response_text) > 1000 else response_text
        }
    
    def _generate_fallback_analysis(self, form_data: Dict) -> Dict:
        """Gera análise de fallback em caso de erro"""
        
        logger.warning("Gerando analise de fallback")
        
        return {
            "avatar_ultra_detalhado": {
                "perfil_demografico": {
                    "segmento": form_data.get('segmento', 'Não informado'),
                    "publico_alvo": form_data.get('publico', 'Não informado')
                },
                "dores_especificas": [
                    "Necessidade de solução específica para o segmento",
                    "Busca por alternativas no mercado",
                    "Desafios específicos do público-alvo"
                ],
                "desejos_profundos": [
                    "Solução eficaz para suas necessidades",
                    "Valor agregado ao investimento",
                    "Resultados mensuráveis"
                ]
            },
            "escopo": {
                "segmento_mercado": form_data.get('segmento', 'Não informado'),
                "produto_servico": form_data.get('produto', 'Não informado'),
                "preco": form_data.get('preco', 'Não informado')
            },
            "analise_concorrencia_detalhada": {
                "concorrentes_principais": form_data.get('concorrentes', 'Análise necessária'),
                "posicionamento": "Análise de posicionamento competitivo"
            },
            "estrategia_palavras_chave": {
                "foco_principal": form_data.get('segmento', ''),
                "estrategia": "Desenvolvimento de estratégia baseada no segmento"
            },
            "metricas_performance_detalhadas": {
                "objetivo_receita": form_data.get('objetivoReceita', 'Não informado'),
                "orcamento_marketing": form_data.get('orcamentoMarketing', 'Não informado')
            },
            "plano_acao_detalhado": {
                "prazo_lancamento": form_data.get('prazoLancamento', 'Não informado'),
                "proximos_passos": "Definir estratégia detalhada baseada nos dados"
            },
            "insights_exclusivos": [
                "Análise personalizada baseada nos dados específicos fornecidos",
                "Estratégia adaptada ao segmento e público-alvo identificado",
                "Recomendações práticas para implementação"
            ],
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "model": "fallback",
                "status": "fallback_analysis"
            }
        }
    
    def test_connection(self) -> bool:
        """Testa conexão com Gemini"""
        try:
            response = self.model.generate_content("Teste de conexão. Responda apenas: OK")
            return bool(response.text and "OK" in response.text.upper())
        except Exception as e:
            logger.error(f"Erro no teste de conexao Gemini: {e}")
            return False


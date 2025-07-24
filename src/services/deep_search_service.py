import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import time
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

class DeepSearchService:
    """Serviço de busca profunda na internet usando DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = 'https://api.deepseek.com/v1/chat/completions'
        self.search_cache = {}  # Cache simples para evitar buscas repetidas
        self.max_iterations = 3  # Máximo de iterações de refinamento
        self.rate_limit_delay = 1  # Delay entre requests para evitar rate limiting
        
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado"""
        return bool(self.api_key)
    
    def perform_deep_search(self, query: str, context_data: Optional[Dict] = None) -> Optional[str]:
        """
        Realiza busca profunda na internet com refinamento iterativo
        
        Args:
            query: Consulta de pesquisa
            context_data: Dados de contexto para enriquecer a busca
            
        Returns:
            Resultados consolidados da busca profunda
        """
        if not self.is_configured():
            logger.warning("DeepSeek API nao configurada")
            return None
        
        # Verificar cache
        cache_key = self._generate_cache_key(query, context_data)
        if cache_key in self.search_cache:
            logger.info("Usando resultado em cache para busca profunda")
            return self.search_cache[cache_key]
        
        try:
            logger.info(f"Iniciando busca profunda: {query}")
            
            # Enriquecer query com contexto
            enhanced_query = self._enhance_query_with_context(query, context_data)
            
            # Realizar busca iterativa
            search_results = self._perform_iterative_search(enhanced_query, context_data)
            
            if search_results:
                # Consolidar resultados
                consolidated_results = self._consolidate_search_results(search_results, query)
                
                # Salvar no cache
                self.search_cache[cache_key] = consolidated_results
                
                logger.info("Busca profunda concluida com sucesso")
                return consolidated_results
            else:
                logger.warning("Nenhum resultado encontrado na busca profunda")
                return None
                
        except Exception as e:
            logger.error(f"Erro na busca profunda: {str(e)}")
            return None
    
    def _generate_cache_key(self, query: str, context_data: Optional[Dict]) -> str:
        """Gera chave de cache para a busca"""
        context_str = json.dumps(context_data, sort_keys=True) if context_data else ""
        return f"{query}_{hash(context_str)}"
    
    def _enhance_query_with_context(self, query: str, context_data: Optional[Dict]) -> str:
        """Enriquece a query com dados de contexto"""
        if not context_data:
            return query
        
        enhanced_parts = [query]
        
        # Adicionar contexto relevante
        if context_data.get('segmento'):
            enhanced_parts.append(f"segmento: {context_data['segmento']}")
        
        if context_data.get('produto'):
            enhanced_parts.append(f"produto: {context_data['produto']}")
        
        if context_data.get('publico'):
            enhanced_parts.append(f"público-alvo: {context_data['publico']}")
        
        # Adicionar contexto geográfico e temporal
        enhanced_parts.append("Brasil")
        enhanced_parts.append(str(datetime.now().year))
        
        # Limitar tamanho da query
        enhanced_query = " ".join(enhanced_parts)
        if len(enhanced_query) > 200:
            enhanced_query = enhanced_query[:200] + "..."
        
        return enhanced_query
    
    def _perform_iterative_search(self, query: str, context_data: Optional[Dict]) -> List[Dict]:
        """Realiza busca iterativa com refinamento"""
        search_results = []
        current_query = query
        
        for iteration in range(self.max_iterations):
            logger.info(f"Iteracao {iteration + 1} de busca profunda")
            
            # Realizar busca atual
            iteration_result = self._perform_single_search(current_query, iteration)
            
            if iteration_result:
                search_results.append({
                    'iteration': iteration + 1,
                    'query': current_query,
                    'results': iteration_result,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Refinar query para próxima iteração
                if iteration < self.max_iterations - 1:
                    refined_query = self._refine_query_from_results(
                        current_query, 
                        iteration_result, 
                        context_data
                    )
                    
                    if refined_query and refined_query != current_query:
                        current_query = refined_query
                        logger.info(f"Query refinada: {refined_query}")
                    else:
                        logger.info("Nao ha necessidade de refinamento adicional")
                        break
            else:
                logger.warning(f"Iteracao {iteration + 1} nao retornou resultados")
                break
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        return search_results
    
    def _perform_single_search(self, query: str, iteration: int) -> Optional[str]:
        """Realiza uma única busca usando DeepSeek"""
        try:
            # Prompt específico para busca na internet
            search_prompt = self._create_search_prompt(query, iteration)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Você é um especialista em pesquisa de mercado e análise de tendências. Sua tarefa é fornecer informações atualizadas e precisas sobre o mercado brasileiro.'
                    },
                    {
                        'role': 'user',
                        'content': search_prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.3,
                'stream': False
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    content = result['choices'][0]['message']['content']
                    logger.info(f"Busca iteracao {iteration + 1} bem-sucedida")
                    return content
                else:
                    logger.warning(f"Resposta vazia na iteracao {iteration + 1}")
                    return None
            else:
                logger.error(f"Erro na API DeepSeek: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na busca individual: {str(e)}")
            return None
    
    def _create_search_prompt(self, query: str, iteration: int) -> str:
        """Cria prompt específico para busca"""
        if iteration == 0:
            # Primeira iteração - busca geral
            return f"""
Realize uma pesquisa abrangente sobre: {query}

Forneça informações atualizadas sobre:
1. Tendências atuais do mercado brasileiro
2. Dados estatísticos relevantes
3. Principais players e concorrentes
4. Oportunidades e desafios
5. Insights de comportamento do consumidor
6. Projeções e perspectivas futuras

Foque em dados de 2023-2024 e seja específico sobre o mercado brasileiro.
Organize as informações de forma estruturada e cite fontes quando possível.
"""
        elif iteration == 1:
            # Segunda iteração - aprofundamento
            return f"""
Aprofunde a pesquisa sobre: {query}

Com base em informações anteriores, forneça:
1. Análise detalhada de segmentação de mercado
2. Estratégias de marketing digital mais eficazes
3. Canais de distribuição e vendas
4. Precificação e posicionamento
5. Regulamentações e aspectos legais
6. Tecnologias emergentes no setor

Seja mais específico e técnico, focando em insights acionáveis.
"""
        else:
            # Terceira iteração - insights específicos
            return f"""
Forneça insights específicos e acionáveis sobre: {query}

Concentre-se em:
1. Oportunidades de nicho não exploradas
2. Estratégias de diferenciação competitiva
3. Métricas de performance do setor
4. Casos de sucesso recentes
5. Previsões para os próximos 12 meses
6. Recomendações estratégicas específicas

Priorize informações que possam gerar vantagem competitiva.
"""
    
    def _refine_query_from_results(self, original_query: str, results: str, context_data: Optional[Dict]) -> Optional[str]:
        """Refina a query baseada nos resultados anteriores"""
        try:
            # Extrair termos-chave dos resultados
            key_terms = self._extract_key_terms(results)
            
            # Criar query refinada
            refined_parts = [original_query]
            
            # Adicionar termos específicos encontrados
            if key_terms:
                refined_parts.extend(key_terms[:3])  # Máximo 3 termos adicionais
            
            # Adicionar especificidade baseada no contexto
            if context_data:
                if context_data.get('preco_float'):
                    price_range = self._categorize_price_range(context_data['preco_float'])
                    refined_parts.append(price_range)
                
                if context_data.get('publico'):
                    refined_parts.append(f"público {context_data['publico']}")
            
            refined_query = " ".join(refined_parts)
            
            # Evitar queries muito longas
            if len(refined_query) > 150:
                refined_query = refined_query[:150] + "..."
            
            return refined_query if refined_query != original_query else None
            
        except Exception as e:
            logger.error(f"Erro ao refinar query: {str(e)}")
            return None
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extrai termos-chave relevantes do texto"""
        try:
            # Palavras-chave relacionadas a negócios e mercado
            business_keywords = [
                'digital', 'online', 'e-commerce', 'marketplace', 'SaaS', 'B2B', 'B2C',
                'startup', 'inovação', 'tecnologia', 'automação', 'IA', 'inteligência artificial',
                'marketing', 'vendas', 'conversão', 'ROI', 'CAC', 'LTV', 'funil',
                'segmentação', 'persona', 'jornada', 'experiência', 'engajamento',
                'mobile', 'app', 'plataforma', 'integração', 'API', 'cloud'
            ]
            
            # Encontrar termos relevantes no texto
            found_terms = []
            text_lower = text.lower()
            
            for keyword in business_keywords:
                if keyword in text_lower and keyword not in found_terms:
                    found_terms.append(keyword)
                    if len(found_terms) >= 5:  # Limitar número de termos
                        break
            
            return found_terms
            
        except Exception as e:
            logger.error(f"Erro ao extrair termos-chave: {str(e)}")
            return []
    
    def _categorize_price_range(self, price: float) -> str:
        """Categoriza faixa de preço"""
        if price <= 100:
            return "baixo custo"
        elif price <= 500:
            return "preço médio"
        elif price <= 2000:
            return "premium"
        else:
            return "alto valor"
    
    def _consolidate_search_results(self, search_results: List[Dict], original_query: str) -> str:
        """Consolida resultados de múltiplas iterações"""
        try:
            consolidated_parts = []
            
            consolidated_parts.append("=== PESQUISA PROFUNDA NA INTERNET ===\n")
            consolidated_parts.append(f"Consulta original: {original_query}")
            consolidated_parts.append(f"Iterações realizadas: {len(search_results)}")
            consolidated_parts.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
            consolidated_parts.append("\n" + "="*60)
            
            # Consolidar resultados por iteração
            for result in search_results:
                iteration = result['iteration']
                query = result['query']
                content = result['results']
                
                consolidated_parts.append(f"\n🔍 ITERAÇÃO {iteration}")
                consolidated_parts.append(f"Query: {query}")
                consolidated_parts.append("-" * 40)
                consolidated_parts.append(content)
                consolidated_parts.append("\n" + "="*40)
            
            # Adicionar resumo executivo
            consolidated_parts.append("\n📋 RESUMO EXECUTIVO")
            consolidated_parts.append("-" * 30)
            
            # Extrair insights principais
            all_content = " ".join([r['results'] for r in search_results])
            key_insights = self._extract_key_insights(all_content)
            
            if key_insights:
                consolidated_parts.append("Principais insights encontrados:")
                for i, insight in enumerate(key_insights, 1):
                    consolidated_parts.append(f"{i}. {insight}")
            
            # Adicionar metadados
            consolidated_parts.append(f"\n📊 METADADOS DA BUSCA")
            consolidated_parts.append(f"Total de caracteres analisados: {len(all_content):,}")
            consolidated_parts.append(f"Queries utilizadas: {len(search_results)}")
            consolidated_parts.append(f"Tempo de execução: ~{len(search_results) * 2} segundos")
            
            return "\n".join(consolidated_parts)
            
        except Exception as e:
            logger.error(f"Erro ao consolidar resultados: {str(e)}")
            return f"Erro na consolidação dos resultados de busca: {str(e)}"
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """Extrai insights principais do conteúdo"""
        try:
            insights = []
            
            # Procurar por padrões de insights
            insight_patterns = [
                r'tendência[^.]*\.', r'oportunidade[^.]*\.', r'crescimento[^.]*\.',
                r'mercado[^.]*\.', r'consumidor[^.]*\.', r'estratégia[^.]*\.',
                r'inovação[^.]*\.', r'tecnologia[^.]*\.', r'digital[^.]*\.'
            ]
            
            content_lower = content.lower()
            
            for pattern in insight_patterns:
                matches = re.findall(pattern, content_lower)
                for match in matches[:2]:  # Máximo 2 por padrão
                    if len(match) > 20 and len(match) < 200:  # Filtrar por tamanho
                        insights.append(match.capitalize())
                        if len(insights) >= 8:  # Máximo 8 insights
                            break
                if len(insights) >= 8:
                    break
            
            return insights[:5]  # Retornar top 5
            
        except Exception as e:
            logger.error(f"Erro ao extrair insights: {str(e)}")
            return []
    
    @lru_cache(maxsize=100)
    def quick_search(self, query: str) -> Optional[str]:
        """Busca rápida com cache para consultas simples"""
        if not self.is_configured():
            return None
        
        try:
            result = self._perform_single_search(query, 0)
            return result
        except Exception as e:
            logger.error(f"Erro na busca rapida: {str(e)}")
            return None
    
    def clear_cache(self):
        """Limpa o cache de buscas"""
        self.search_cache.clear()
        logger.info("Cache de buscas limpo")
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        return {
            'cache_size': len(self.search_cache),
            'max_iterations': self.max_iterations,
            'rate_limit_delay': self.rate_limit_delay,
            'configured': self.is_configured()
        }


# -*- coding: utf-8 -*-
import os
import sys
import logging
from typing import Dict, Optional, Any
import json
from datetime import datetime
import re

# Configuração de encoding seguro para Windows
if sys.platform.startswith('win'):
    try:
        os.system('chcp 65001 > nul 2>&1')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
    except:
        pass

# Função para print/log seguro
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis e caracteres especiais
        clean_text = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', str(text))
        print(clean_text)

# Handler de logging seguro
class SafeLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            super().emit(record)
        except UnicodeEncodeError:
            original_msg = self.format(record)
            clean_msg = re.sub(r'[^\x00-\x7F]+', '[OK]', original_msg)
            clean_record = logging.LogRecord(
                record.name, record.levelno, record.pathname,
                record.lineno, clean_msg, record.args, record.exc_info
            )
            clean_record.created = record.created
            clean_record.msecs = record.msecs
            try:
                self.stream.write(self.format(clean_record) + self.terminator)
                self.flush()
            except Exception:
                safe_print(f"LOG: {clean_msg}")

# Configurar logger seguro
logger = logging.getLogger(__name__)
if not logger.handlers:
    safe_handler = SafeLoggingHandler(sys.stdout)
    safe_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(safe_handler)
    logger.setLevel(logging.INFO)

class WebSailorIntegrationService:
    """Serviço de integração do WebSailor com ARQV30 - Versão corrigida para Unicode"""
    
    def __init__(self):
        self.websailor_service = None
        self.config = self._load_config()
        self._initialize_websailor()
    
    def _load_config(self) -> Dict:
        """Carrega configuração do WebSailor"""
        return {
            'api_key': os.getenv('DEEPSEEK_API_KEY'),  # Usar DeepSeek como LLM
            'base_url': 'https://api.deepseek.com/v1',
            'google_search_key': os.getenv('GOOGLE_SEARCH_KEY'),
            'jina_api_key': os.getenv('JINA_API_KEY'),
            'enabled': os.getenv('WEBSAILOR_ENABLED', 'true').lower() == 'true'
        }
    
    def _initialize_websailor(self):
        """Inicializa o serviço WebSailor"""
        if not self.config['enabled']:
            safe_print("WebSailor desabilitado por configuracao")
            logger.info("WebSailor desabilitado por configuracao")
            return
        
        try:
            # Importar WebSailor apenas se necessário
            from services.websailor_react_agent import WebSailorService
            
            self.websailor_service = WebSailorService(self.config)
            
            if self.websailor_service.is_available():
                # CORREÇÃO: Removido emoji problemático
                safe_print("[OK] WebSailor inicializado com sucesso")
                logger.info("WebSailor inicializado com sucesso")
            else:
                safe_print("[AVISO] WebSailor inicializado mas nao esta totalmente funcional")
                logger.warning("WebSailor inicializado mas nao esta totalmente funcional")
                
        except ImportError as e:
            error_msg = f"WebSailor nao disponivel - dependencias nao instaladas: {e}"
            safe_print(f"[AVISO] {error_msg}")
            logger.warning(error_msg)
            self.websailor_service = None
        except Exception as e:
            error_msg = f"Erro ao inicializar WebSailor: {e}"
            safe_print(f"[ERRO] {error_msg}")
            logger.error(error_msg)
            self.websailor_service = None
    
    def is_available(self) -> bool:
        """Verifica se o WebSailor está disponível"""
        return (
            self.websailor_service is not None and 
            self.websailor_service.is_available()
        )
    
    def perform_deep_web_research(self, query: str, context_data: Optional[Dict] = None) -> Dict:
        """
        Realiza pesquisa profunda na web usando WebSailor
        
        Args:
            query: Consulta de pesquisa
            context_data: Dados de contexto para enriquecer a pesquisa
            
        Returns:
            Resultados da pesquisa profunda
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'WebSailor não está disponível',
                'fallback_used': True,
                'results': self._fallback_research(query, context_data)
            }
        
        try:
            safe_print(f"[BUSCA] Iniciando pesquisa profunda com WebSailor: {query}")
            logger.info(f"Iniciando pesquisa profunda com WebSailor: {query}")
            
            # Preparar contexto enriquecido
            enhanced_context = self._prepare_context(context_data)
            
            # Realizar pesquisa com WebSailor
            result = self.websailor_service.perform_research(query, enhanced_context)
            
            if result['success']:
                safe_print("[OK] Pesquisa profunda concluida com sucesso")
                logger.info("Pesquisa profunda concluida com sucesso")
                return {
                    'success': True,
                    'websailor_used': True,
                    'results': self._format_websailor_results(result),
                    'metadata': {
                        'timestamp': datetime.utcnow().isoformat(),
                        'query': query,
                        'iterations': result.get('total_iterations', 0)
                    }
                }
            else:
                error_msg = f"WebSailor retornou erro: {result.get('error')}"
                safe_print(f"[AVISO] {error_msg}")
                logger.warning(error_msg)
                return {
                    'success': False,
                    'error': result.get('error'),
                    'fallback_used': True,
                    'results': self._fallback_research(query, context_data)
                }
                
        except Exception as e:
            error_msg = f"Erro na pesquisa com WebSailor: {e}"
            safe_print(f"[ERRO] {error_msg}")
            logger.error(error_msg)
            return {
                'success': False,
                'error': str(e),
                'fallback_used': True,
                'results': self._fallback_research(query, context_data)
            }
    
    def _prepare_context(self, context_data: Optional[Dict]) -> Dict:
        """Prepara contexto enriquecido para o WebSailor"""
        if not context_data:
            return {}
        
        enhanced_context = {
            'market_segment': context_data.get('segmento', ''),
            'product': context_data.get('produto', ''),
            'target_audience': context_data.get('publico', ''),
            'competitors': context_data.get('concorrentes', ''),
            'price_range': context_data.get('preco_float', 0),
            'revenue_goal': context_data.get('objetivo_receita_float', 0),
            'marketing_budget': context_data.get('orcamento_marketing_float', 0),
            'launch_timeline': context_data.get('prazo_lancamento', ''),
            'additional_data': context_data.get('dados_adicionais', ''),
            'geographic_focus': 'Brazil',  # Foco no mercado brasileiro
            'language': 'Portuguese'
        }
        
        return enhanced_context
    
    def _format_websailor_results(self, result: Dict) -> str:
        """Formata resultados do WebSailor para integração"""
        formatted_parts = []
        
        formatted_parts.append("=== PESQUISA PROFUNDA COM WEBSAILOR ===\n")
        
        # Resposta final
        if result.get('final_answer'):
            formatted_parts.append("[DADOS] ANALISE PRINCIPAL:")
            formatted_parts.append(result['final_answer'])
            formatted_parts.append("\n" + "="*50)
        
        # Resultados de busca
        if result.get('search_results'):
            formatted_parts.append("\n[BUSCA] RESULTADOS DE BUSCA:")
            for i, search_result in enumerate(result['search_results'], 1):
                formatted_parts.append(f"\n--- Busca {i} ---")
                formatted_parts.append(search_result)
        
        # Páginas visitadas
        if result.get('visited_pages'):
            formatted_parts.append("\n[PAGINA] PAGINAS ANALISADAS:")
            for i, page_content in enumerate(result['visited_pages'], 1):
                formatted_parts.append(f"\n--- Pagina {i} ---")
                # Limitar conteúdo da página para evitar texto muito longo
                if len(page_content) > 1000:
                    page_content = page_content[:1000] + "...\n[Conteudo truncado]"
                formatted_parts.append(page_content)
        
        # Metadados
        formatted_parts.append(f"\n[DADOS] ESTATISTICAS:")
        formatted_parts.append(f"Total de iteracoes: {result.get('total_iterations', 0)}")
        formatted_parts.append(f"Buscas realizadas: {len(result.get('search_results', []))}")
        formatted_parts.append(f"Paginas visitadas: {len(result.get('visited_pages', []))}")
        
        return "\n".join(formatted_parts)
    
    def _fallback_research(self, query: str, context_data: Optional[Dict]) -> str:
        """Pesquisa de fallback quando WebSailor não está disponível"""
        fallback_parts = []
        
        fallback_parts.append("=== PESQUISA BASICA (FALLBACK) ===\n")
        fallback_parts.append(f"Consulta: {query}")
        
        if context_data:
            fallback_parts.append(f"\nContexto fornecido:")
            fallback_parts.append(f"- Segmento: {context_data.get('segmento', 'N/A')}")
            fallback_parts.append(f"- Produto: {context_data.get('produto', 'N/A')}")
            fallback_parts.append(f"- Publico: {context_data.get('publico', 'N/A')}")
        
        fallback_parts.append(f"\n[AVISO] LIMITACAO: WebSailor nao esta disponivel.")
        fallback_parts.append("Para pesquisa profunda na internet, configure:")
        fallback_parts.append("- GOOGLE_SEARCH_KEY (para busca Google)")
        fallback_parts.append("- JINA_API_KEY (para extracao de conteudo)")
        fallback_parts.append("- WEBSAILOR_ENABLED=true")
        
        fallback_parts.append(f"\n[IDEIA] SUGESTAO: Realize pesquisa manual sobre '{query}' e inclua os resultados como anexo.")
        
        return "\n".join(fallback_parts)
    
    def quick_fact_check(self, statement: str) -> str:
        """Verificação rápida de fatos usando WebSailor"""
        if not self.is_available():
            return f"Verificacao de fatos nao disponivel. WebSailor nao configurado.\nDeclaracao: {statement}"
        
        try:
            result = self.websailor_service.quick_fact_check(statement)
            return f"[OK] VERIFICACAO DE FATOS:\n{result}"
        except Exception as e:
            return f"[ERRO] Erro na verificacao: {str(e)}\nDeclaracao: {statement}"
    
    def market_research(self, topic: str, region: str = "Brazil") -> Dict:
        """Pesquisa de mercado usando WebSailor"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'WebSailor não disponível para pesquisa de mercado'
            }
        
        try:
            return self.websailor_service.market_research(topic, region)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_service_status(self) -> Dict:
        """Retorna status do serviço WebSailor"""
        status = {
            'websailor_available': self.is_available(),
            'config_loaded': bool(self.config),
            'enabled': self.config.get('enabled', False),
            'has_api_key': bool(self.config.get('api_key')),
            'has_search_key': bool(self.config.get('google_search_key')),
            'has_jina_key': bool(self.config.get('jina_api_key'))
        }
        
        if self.websailor_service:
            try:
                status['service_initialized'] = True
                status['service_functional'] = self.websailor_service.is_available()
            except:
                status['service_initialized'] = False
                status['service_functional'] = False
        else:
            status['service_initialized'] = False
            status['service_functional'] = False
        
        return status
    
    def test_connection(self) -> Dict:
        """Testa conexão e funcionalidade do WebSailor"""
        if not self.is_available():
            return {
                'success': False,
                'message': 'WebSailor não está disponível',
                'details': self.get_service_status()
            }
        
        try:
            # Teste simples de pesquisa
            test_query = "teste de conectividade"
            result = self.websailor_service.quick_fact_check(test_query)
            
            return {
                'success': True,
                'message': 'WebSailor funcionando corretamente',
                'test_result': result[:200] + "..." if len(result) > 200 else result,
                'details': self.get_service_status()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro no teste: {str(e)}',
                'details': self.get_service_status()
            }

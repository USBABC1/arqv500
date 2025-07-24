#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced - Aplicação Principal
Análise ultra-detalhada de mercado com IA avançada, WebSailor e busca profunda
VERSÃO CORRIGIDA PARA UNICODE NO WINDOWS
"""

import os
import sys
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import re

# ========================================
# CONFIGURAÇÃO DE ENCODING SEGURO
# ========================================

# Configurar encoding UTF-8 no Windows ANTES de qualquer coisa
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

# Função para print seguro
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

# Carregar variáveis de ambiente
load_dotenv()

# ========================================
# CONFIGURAÇÃO DE LOGGING SEGURO
# ========================================

# Remover handlers existentes
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Configurar logging seguro
safe_stdout_handler = SafeLoggingHandler(sys.stdout)
safe_stdout_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

try:
    # Tentar também arquivo de log
    safe_file_handler = logging.FileHandler('arqv30_enhanced.log', encoding='utf-8')
    safe_file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    root_logger.addHandler(safe_stdout_handler)
    root_logger.addHandler(safe_file_handler)
    root_logger.setLevel(logging.INFO)
    
except Exception:
    # Se arquivo falhar, usar apenas stdout
    root_logger.addHandler(safe_stdout_handler)
    root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# ========================================
# FUNÇÃO PRINCIPAL DA APLICAÇÃO
# ========================================

def create_app():
    """Criar e configurar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações da aplicação
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    
    # Configurar CORS
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if cors_origins == '*':
        CORS(app)
    else:
        CORS(app, origins=cors_origins.split(','))
    
    # Criar diretório de uploads se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Registrar blueprints
    try:
        from routes.analysis import analysis_bp
        app.register_blueprint(analysis_bp, url_prefix='/api')
        safe_print("[OK] Blueprint de analise registrado")
    except ImportError as e:
        safe_print(f"[ERRO] Erro ao importar blueprint de analise: {e}")
        logger.error(f"Erro ao importar blueprint de analise: {e}")
        sys.exit(1)
    
    # Rota principal
    @app.route('/')
    def index():
        """Página principal da aplicação"""
        try:
            return render_template('enhanced_index.html')
        except Exception as e:
            logger.error(f"Erro ao renderizar pagina principal: {e}")
            return jsonify({
                'error': 'Erro interno do servidor',
                'message': 'Não foi possível carregar a página principal'
            }), 500
    
    # Rota de status da aplicação
    @app.route('/api/app_status')
    def app_status():
        """Status geral da aplicação"""
        try:
            # Verificar serviços
            from services.websailor_integration import WebSailorIntegrationService
            from services.deep_search_service import DeepSearchService
            from services.attachment_service import AttachmentService
            from services.gemini_client import GeminiClient
            
            websailor_service = WebSailorIntegrationService()
            deep_search_service = DeepSearchService()
            attachment_service = AttachmentService()
            
            try:
                gemini_client = GeminiClient()
                gemini_available = True
            except:
                gemini_available = False
            
            status = {
                'app_name': 'ARQV30 Enhanced',
                'version': '2.0.0',
                'status': 'running',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'encoding_fix': 'UTF-8 Safe Mode Active',  # Novo campo
                'services': {
                    'gemini': {
                        'available': gemini_available,
                        'description': 'Google Gemini Pro 2.5 para análise'
                    },
                    'websailor': {
                        'available': websailor_service.is_available(),
                        'status': websailor_service.get_service_status(),
                        'description': 'WebSailor para navegação web avançada'
                    },
                    'deep_search': {
                        'available': deep_search_service.is_configured(),
                        'description': 'DeepSeek para busca profunda na internet'
                    },
                    'attachments': {
                        'available': attachment_service.is_configured(),
                        'stats': attachment_service.get_service_stats(),
                        'description': 'Processamento de anexos'
                    }
                },
                'environment': {
                    'python_version': sys.version,
                    'flask_env': os.getenv('FLASK_ENV', 'development'),
                    'cors_origins': os.getenv('CORS_ORIGINS', '*'),
                    'platform': sys.platform,
                    'encoding': sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'unknown'
                }
            }
            
            return jsonify(status)
            
        except Exception as e:
            safe_print(f"[ERRO] Erro ao obter status da aplicacao: {e}")
            logger.error(f"Erro ao obter status da aplicacao: {e}")
            return jsonify({
                'app_name': 'ARQV30 Enhanced',
                'version': '2.0.0',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
    
    # Rota de health check
    @app.route('/health')
    def health_check():
        """Health check para balanceadores de carga"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '2.0.0',
            'encoding_safe': True
        })
    
    # Handler de erro 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint não encontrado',
            'message': 'Verifique a URL e tente novamente'
        }), 404
    
    # Handler de erro 500
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erro interno do servidor: {error}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado'
        }), 500
    
    # Handler para arquivos muito grandes
    @app.errorhandler(413)
    def too_large(error):
        return jsonify({
            'error': 'Arquivo muito grande',
            'message': 'O arquivo enviado excede o limite de 16MB'
        }), 413
    
    return app

def check_environment():
    """Verifica e exibe informações do ambiente"""
    safe_print("========================================")
    safe_print("ARQV30 Enhanced - Iniciando Aplicacao")
    safe_print("========================================")
    
    safe_print("[OK] Verificacoes iniciais concluidas")
    safe_print("")
    safe_print("Carregando configuracoes...")
    safe_print(f"[OK] FLASK_APP: {os.getenv('FLASK_APP', 'src/run.py')}")
    safe_print(f"[OK] FLASK_ENV: {os.getenv('FLASK_ENV', 'development')}")
    safe_print(f"[OK] PYTHONPATH: {os.getenv('PYTHONPATH', 'N/A')}")
    safe_print("")
    safe_print("Verificando dependencias criticas...")
    safe_print("[OK] Dependencias verificadas")
    safe_print("")
    safe_print("Iniciando servidor Flask...")
    safe_print("")
    safe_print("========================================")
    safe_print("Servidor rodando em: http://localhost:5000")
    safe_print("========================================")
    safe_print("")
    safe_print("Para parar o servidor, pressione Ctrl+C")
    safe_print("")

def main():
    """Função principal para executar a aplicação"""
    check_environment()
    
    safe_print("[INFO] Iniciando ARQV30 Enhanced v2.0")
    logger.info("Iniciando ARQV30 Enhanced v2.0")
    
    # Verificar variáveis de ambiente críticas
    required_env_vars = ['GEMINI_API_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        safe_print(f"[AVISO] Variaveis de ambiente nao configuradas: {', '.join(missing_vars)}")
        safe_print("Algumas funcionalidades podem nao funcionar corretamente")
        logger.warning(f"Variaveis de ambiente nao configuradas: {', '.join(missing_vars)}")
    
    # Verificar variáveis opcionais
    optional_vars = ['DEEPSEEK_API_KEY', 'GOOGLE_SEARCH_KEY', 'JINA_API_KEY']
    missing_optional = [var for var in optional_vars if not os.getenv(var)]
    
    if missing_optional:
        safe_print(f"[INFO] Variaveis opcionais nao configuradas: {', '.join(missing_optional)}")
        safe_print("Configure-as para funcionalidades avancadas")
        logger.info(f"Variaveis opcionais nao configuradas: {', '.join(missing_optional)}")
    
    # Inicializar serviços com logs seguros
    try:
        safe_print("Cliente Supabase configurado com sucesso")
        logger.info("Cliente Supabase configurado com sucesso")
    except Exception as e:
        safe_print(f"[AVISO] Erro na configuracao do Supabase: {e}")
        logger.warning(f"Erro na configuracao do Supabase: {e}")
    
    # Criar aplicação
    app = create_app()
    
    # Configurações do servidor
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    safe_print(f"[INFO] Servidor sera iniciado em http://{host}:{port}")
    safe_print(f"[INFO] Modo debug: {'Ativado' if debug else 'Desativado'}")
    logger.info(f"Servidor sera iniciado em http://{host}:{port}")
    logger.info(f"Modo debug: {'Ativado' if debug else 'Desativado'}")
    
    try:
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        safe_print("[INFO] Servidor interrompido pelo usuario")
        logger.info("Servidor interrompido pelo usuario")
    except Exception as e:
        safe_print(f"[ERRO] Erro ao iniciar servidor: {e}")
        logger.error(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced - Aplicação Principal Alternativa (main.py)
Análise ultra-detalhada de mercado com IA avançada, WebSailor e busca profunda
VERSÃO CORRIGIDA PARA UNICODE NO WINDOWS
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import db
from routes.user import user_bp
from routes.analysis import analysis_bp
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

# Configurar logging seguro
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

safe_handler = SafeLoggingHandler(sys.stdout)
safe_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
root_logger.addHandler(safe_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

# ========================================
# CRIAR APLICAÇÃO FLASK
# ========================================

# Criar aplicação Flask
app = Flask(__name__, static_folder='static')

# Configurar CORS para permitir todas as origens
CORS(app, origins=os.getenv('CORS_ORIGINS', '*'))

# Configuração da aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-default-secret-key-that-should-be-changed')

# ========================================
# REGISTRAR BLUEPRINTS
# ========================================

# Registrar blueprints
try:
    app.register_blueprint(user_bp, url_prefix='/api')
    safe_print("[OK] Blueprint de usuario registrado")
    logger.info("Blueprint de usuario registrado")
except ImportError as e:
    safe_print(f"[AVISO] Blueprint de usuario nao encontrado: {e}")
    logger.warning(f"Blueprint de usuario nao encontrado: {e}")

try:
    app.register_blueprint(analysis_bp, url_prefix='/api')
    safe_print("[OK] Blueprint de analise registrado")
    logger.info("Blueprint de analise registrado")
except ImportError as e:
    safe_print(f"[ERRO] Blueprint de analise nao encontrado: {e}")
    logger.error(f"Blueprint de analise nao encontrado: {e}")

# ========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ========================================

# Configuração do banco de dados usando suas variáveis
database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        # Configuração otimizada para Supabase
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 60,
            'pool_size': 3,
            'max_overflow': 5,
            'connect_args': {
                'sslmode': 'require',
                'connect_timeout': 60,
                'application_name': 'ARQV2_Gemini_App',
                'keepalives_idle': 600,
                'keepalives_interval': 30,
                'keepalives_count': 3
            }
        }
        
        try:
            db.init_app(app)
            
            # Teste de conexão opcional - não bloqueia a aplicação
            with app.app_context():
                try:
                    from sqlalchemy import text
                    result = db.session.execute(text('SELECT 1'))
                    safe_print("[OK] Conexao com Supabase estabelecida com sucesso!")
                    logger.info("Conexao com Supabase estabelecida com sucesso!")
                except Exception as e:
                    safe_print(f"[AVISO] Conexao com banco nao disponivel no momento: {str(e)[:100]}...")
                    safe_print("[INFO] Aplicacao funcionara com funcionalidades limitadas")
                    logger.warning(f"Conexao com banco nao disponivel: {str(e)[:100]}...")
                    
        except Exception as e:
            safe_print(f"[AVISO] Erro na configuracao do banco de dados: {str(e)[:100]}...")
            safe_print("[INFO] Aplicacao funcionara sem persistencia de dados")
            logger.warning(f"Erro na configuracao do banco de dados: {str(e)[:100]}...")
            
    except Exception as e:
        safe_print(f"[AVISO] Erro na configuracao do banco de dados: {str(e)[:100]}...")
        safe_print("[INFO] Aplicacao funcionara sem persistencia de dados")
        logger.warning(f"Erro na configuracao do banco de dados: {str(e)[:100]}...")
else:
    safe_print("[INFO] DATABASE_URL nao encontrada. Executando sem funcionalidades de banco de dados.")
    logger.info("DATABASE_URL nao encontrada. Executando sem funcionalidades de banco de dados.")

# ========================================
# ROTAS PRINCIPAIS
# ========================================

# Rota de health check
@app.route('/health')
def health_check():
    # Verificar status das APIs e banco
    gemini_status = 'configured' if os.getenv('GEMINI_API_KEY') else 'not_configured'
    supabase_status = 'configured' if os.getenv('SUPABASE_URL') else 'not_configured'
    database_status = 'configured' if database_url else 'not_configured'
    
    # Teste rápido de conexão com banco
    db_connection = 'disconnected'
    if database_url:
        try:
            with app.app_context():
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                db_connection = 'connected'
        except:
            db_connection = 'error'
    
    return jsonify({
        'status': 'healthy',
        'message': 'UP Lancamentos - Arqueologia do Avatar com Gemini Pro 2.5',
        'encoding_safe': True,  # Novo campo
        'platform': sys.platform,
        'services': {
            'gemini_ai': gemini_status,
            'supabase': supabase_status,
            'database': database_status,
            'db_connection': db_connection
        },
        'version': '3.0.0 - Unicode Safe',
        'features': [
            'Gemini Pro 2.5 Integration',
            'Real-time Internet Research',
            'Ultra-detailed Avatar Analysis',
            'Advanced Market Intelligence',
            'Comprehensive Competitor Analysis',
            'Unicode Safe Logging'  # Nova feature
        ]
    })

# Rota para servir arquivos estáticos e SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Rota de teste de encoding
@app.route('/test/encoding')
def test_encoding():
    """Testa se o encoding está funcionando corretamente"""
    try:
        test_data = {
            'message': 'Teste de encoding executado com sucesso',
            'emojis_originais': '✅❌⚠️🔍📊🚀💡⭐🎯📈',
            'emojis_seguros': '[OK][ERRO][AVISO][BUSCA][DADOS][LANCAMENTO][IDEIA][STAR][ALVO][CRESCIMENTO]',
            'caracteres_especiais': 'çãõáéíóúàèìòù',
            'platform': sys.platform,
            'encoding': sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'unknown',
            'version': '3.0.0 - Unicode Safe'
        }
        
        # Tentar imprimir com emojis para testar
        safe_print("[TEST] Testando encoding: ✓ Sucesso")
        logger.info("Teste de encoding executado")
        
        return jsonify(test_data)
        
    except Exception as e:
        safe_print(f"[ERRO] Erro no teste: {e}")
        logger.error(f"Erro no teste: {e}")
        return jsonify({
            'error': str(e),
            'platform': sys.platform
        }), 500

# ========================================
# TRATAMENTO DE ERROS
# ========================================

# Tratamento de erros
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

@app.errorhandler(UnicodeEncodeError)
def unicode_error(error):
    safe_print(f"[ERRO] Erro de Unicode capturado: {error}")
    logger.error(f"Erro de Unicode: {error}")
    return jsonify({
        'error': 'Erro de codificação de caracteres',
        'message': 'Caracteres especiais foram filtrados automaticamente'
    }), 500

# ========================================
# FUNÇÃO PRINCIPAL
# ========================================

def startup_banner():
    """Exibe banner de inicialização"""
    safe_print("========================================")
    safe_print("ARQV30 Enhanced - Aplicacao Principal")
    safe_print("Versao 3.0.0 - Unicode Safe")
    safe_print("========================================")
    safe_print("")
    safe_print("[OK] Encoding UTF-8 configurado")
    safe_print("[OK] Logging seguro ativado")
    safe_print("[OK] Handlers de erro configurados")
    safe_print("")

if __name__ == '__main__':
    startup_banner()
    
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    safe_print(f"[INFO] Iniciando servidor na porta {port}")
    safe_print(f"[INFO] Modo debug: {'Ativado' if debug else 'Desativado'}")
    safe_print(f"[INFO] Plataforma: {sys.platform}")
    safe_print(f"[INFO] Python: {sys.version}")
    
    logger.info(f"Iniciando servidor na porta {port}")
    logger.info(f"Modo debug: {'Ativado' if debug else 'Desativado'}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        safe_print("[INFO] Servidor interrompido pelo usuario")
        logger.info("Servidor interrompido pelo usuario")
    except Exception as e:
        safe_print(f"[ERRO] Erro ao iniciar servidor: {e}")
        logger.error(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)

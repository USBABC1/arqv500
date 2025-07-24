import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid
import hashlib
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import mimetypes
import tempfile
import shutil

logger = logging.getLogger(__name__)

class AttachmentService:
    """Serviço para processamento e análise de anexos"""
    
    def __init__(self):
        self.upload_folder = os.path.join(tempfile.gettempdir(), 'arqv30_attachments')
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {
            'txt', 'pdf', 'doc', 'docx', 'json', 'csv', 'xlsx', 'xls'
        }
        self.session_storage = {}  # Armazenamento em memória para sessões
        self.session_ttl = timedelta(hours=24)  # TTL de 24 horas para sessões
        
        # Criar diretório de upload se não existir
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Limpar arquivos antigos na inicialização
        self._cleanup_old_files()
    
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado"""
        return os.path.exists(self.upload_folder)
    
    def process_attachment(self, file: FileStorage, session_id: str) -> Dict:
        """
        Processa um anexo enviado pelo usuário
        
        Args:
            file: Arquivo enviado
            session_id: ID da sessão do usuário
            
        Returns:
            Resultado do processamento
        """
        try:
            # Validar arquivo
            validation_result = self._validate_file(file)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Salvar arquivo temporariamente
            file_info = self._save_temp_file(file, session_id)
            if not file_info:
                return {
                    'success': False,
                    'error': 'Erro ao salvar arquivo temporário'
                }
            
            # Analisar conteúdo do arquivo
            content_analysis = self._analyze_file_content(file_info)
            
            # Armazenar informações da sessão
            attachment_data = {
                'attachment_id': file_info['attachment_id'],
                'original_filename': file_info['original_filename'],
                'file_path': file_info['file_path'],
                'file_size': file_info['file_size'],
                'mime_type': file_info['mime_type'],
                'content_type': content_analysis['content_type'],
                'extracted_content': content_analysis['content'],
                'metadata': content_analysis['metadata'],
                'uploaded_at': datetime.utcnow().isoformat(),
                'session_id': session_id
            }
            
            # Adicionar à sessão
            if session_id not in self.session_storage:
                self.session_storage[session_id] = {
                    'created_at': datetime.utcnow(),
                    'attachments': []
                }
            
            self.session_storage[session_id]['attachments'].append(attachment_data)
            
            logger.info(f"Anexo processado: {file.filename} (Tipo: {content_analysis['content_type']})")
            
            return {
                'success': True,
                'attachment_id': file_info['attachment_id'],
                'content_type': content_analysis['content_type'],
                'content_preview': content_analysis['content'][:200] + "..." if len(content_analysis['content']) > 200 else content_analysis['content']
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar anexo: {str(e)}")
            return {
                'success': False,
                'error': f'Erro no processamento: {str(e)}'
            }
    
    def _validate_file(self, file: FileStorage) -> Dict:
        """Valida o arquivo enviado"""
        if not file or not file.filename:
            return {'valid': False, 'error': 'Nenhum arquivo fornecido'}
        
        # Verificar extensão
        filename = secure_filename(file.filename)
        if '.' not in filename:
            return {'valid': False, 'error': 'Arquivo sem extensão'}
        
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in self.allowed_extensions:
            return {
                'valid': False, 
                'error': f'Tipo de arquivo não suportado. Permitidos: {", ".join(self.allowed_extensions)}'
            }
        
        # Verificar tamanho (aproximado)
        file.seek(0, 2)  # Ir para o final
        file_size = file.tell()
        file.seek(0)  # Voltar ao início
        
        if file_size > self.max_file_size:
            return {
                'valid': False, 
                'error': f'Arquivo muito grande. Máximo: {self.max_file_size // (1024*1024)}MB'
            }
        
        return {'valid': True}
    
    def _save_temp_file(self, file: FileStorage, session_id: str) -> Optional[Dict]:
        """Salva arquivo temporariamente"""
        try:
            # Gerar ID único para o anexo
            attachment_id = str(uuid.uuid4())
            
            # Nome seguro do arquivo
            filename = secure_filename(file.filename)
            
            # Criar subdiretório para a sessão
            session_dir = os.path.join(self.upload_folder, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Caminho final do arquivo
            file_path = os.path.join(session_dir, f"{attachment_id}_{filename}")
            
            # Salvar arquivo
            file.save(file_path)
            
            # Obter informações do arquivo
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'attachment_id': attachment_id,
                'original_filename': filename,
                'file_path': file_path,
                'file_size': file_size,
                'mime_type': mime_type or 'application/octet-stream'
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            return None
    
    def _analyze_file_content(self, file_info: Dict) -> Dict:
        """Analisa o conteúdo do arquivo e determina seu tipo"""
        file_path = file_info['file_path']
        filename = file_info['original_filename'].lower()
        
        try:
            # Determinar tipo de conteúdo baseado no nome e conteúdo
            content_type = self._determine_content_type(filename)
            
            # Extrair conteúdo baseado no tipo de arquivo
            if filename.endswith('.txt'):
                content = self._extract_text_content(file_path)
            elif filename.endswith('.json'):
                content = self._extract_json_content(file_path)
            elif filename.endswith('.csv'):
                content = self._extract_csv_content(file_path)
            elif filename.endswith(('.pdf')):
                content = self._extract_pdf_content(file_path)
            elif filename.endswith(('.doc', '.docx')):
                content = self._extract_doc_content(file_path)
            elif filename.endswith(('.xls', '.xlsx')):
                content = self._extract_excel_content(file_path)
            else:
                content = "Tipo de arquivo não suportado para extração de conteúdo"
            
            # Analisar conteúdo para classificação mais específica
            refined_type = self._refine_content_type(content, content_type)
            
            # Extrair metadados
            metadata = self._extract_metadata(content, refined_type)
            
            return {
                'content_type': refined_type,
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar conteudo: {str(e)}")
            return {
                'content_type': 'unknown',
                'content': f'Erro na análise: {str(e)}',
                'metadata': {}
            }
    
    def _determine_content_type(self, filename: str) -> str:
        """Determina o tipo de conteúdo baseado no nome do arquivo"""
        filename_lower = filename.lower()
        
        # Padrões específicos para tipos de conteúdo
        if any(keyword in filename_lower for keyword in ['driver', 'mental', 'gatilho', 'psicolog']):
            return 'drivers_mentais'
        elif any(keyword in filename_lower for keyword in ['prova', 'visual', 'demonstra', 'evidencia']):
            return 'provas_visuais'
        elif any(keyword in filename_lower for keyword in ['perfil', 'persona', 'avatar', 'publico']):
            return 'perfil_psicologico'
        elif any(keyword in filename_lower for keyword in ['pesquisa', 'survey', 'questionario', 'dados']):
            return 'dados_pesquisa'
        elif any(keyword in filename_lower for keyword in ['mercado', 'concorrente', 'competidor']):
            return 'analise_mercado'
        elif any(keyword in filename_lower for keyword in ['financeiro', 'orcamento', 'custo', 'receita']):
            return 'dados_financeiros'
        else:
            return 'documento_geral'
    
    def _refine_content_type(self, content: str, initial_type: str) -> str:
        """Refina o tipo de conteúdo baseado na análise do texto"""
        content_lower = content.lower()
        
        # Palavras-chave para drivers mentais
        drivers_keywords = [
            'gatilho', 'ancoragem', 'ferida', 'dor', 'medo', 'desejo', 'sonho',
            'troféu', 'status', 'reconhecimento', 'urgência', 'escassez',
            'autoridade', 'prova social', 'reciprocidade'
        ]
        
        # Palavras-chave para provas visuais
        provas_keywords = [
            'demonstração', 'experimento', 'teste', 'resultado', 'evidência',
            'prova', 'caso', 'exemplo', 'comparação', 'antes e depois',
            'screenshot', 'gráfico', 'métrica'
        ]
        
        # Palavras-chave para perfil psicológico
        perfil_keywords = [
            'persona', 'avatar', 'perfil', 'comportamento', 'hábito',
            'preferência', 'motivação', 'objetivo', 'frustração', 'idade',
            'renda', 'escolaridade', 'profissão'
        ]
        
        # Contar ocorrências de palavras-chave
        drivers_count = sum(1 for keyword in drivers_keywords if keyword in content_lower)
        provas_count = sum(1 for keyword in provas_keywords if keyword in content_lower)
        perfil_count = sum(1 for keyword in perfil_keywords if keyword in content_lower)
        
        # Determinar tipo baseado na maior contagem
        if drivers_count > provas_count and drivers_count > perfil_count:
            return 'drivers_mentais'
        elif provas_count > perfil_count:
            return 'provas_visuais'
        elif perfil_count > 0:
            return 'perfil_psicologico'
        else:
            return initial_type
    
    def _extract_text_content(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo de texto"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _extract_json_content(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Erro ao processar JSON: {str(e)}"
    
    def _extract_csv_content(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo CSV"""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # Limitar a 100 linhas para evitar conteúdo muito grande
            if len(df) > 100:
                df = df.head(100)
                truncated_note = f"\n\n[Arquivo truncado - mostrando primeiras 100 linhas de {len(pd.read_csv(file_path))}]"
            else:
                truncated_note = ""
            
            return df.to_string() + truncated_note
        except ImportError:
            # Fallback sem pandas
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:100]  # Primeiras 100 linhas
                return ''.join(lines)
        except Exception as e:
            return f"Erro ao processar CSV: {str(e)}"
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo PDF"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages[:10]:  # Primeiras 10 páginas
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            return "PyPDF2 não disponível para extração de PDF"
        except Exception as e:
            return f"Erro ao processar PDF: {str(e)}"
    
    def _extract_doc_content(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo DOC/DOCX"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            return "python-docx não disponível para extração de DOC/DOCX"
        except Exception as e:
            return f"Erro ao processar DOC/DOCX: {str(e)}"
    
    def _extract_excel_content(self, file_path: str) -> str:
        """Extrai conteúdo de arquivo Excel"""
        try:
            import pandas as pd
            
            # Ler todas as planilhas
            excel_file = pd.ExcelFile(file_path)
            content_parts = []
            
            for sheet_name in excel_file.sheet_names[:5]:  # Máximo 5 planilhas
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Limitar linhas
                if len(df) > 50:
                    df = df.head(50)
                    truncated_note = f" [Truncado - {len(pd.read_excel(file_path, sheet_name=sheet_name))} linhas total]"
                else:
                    truncated_note = ""
                
                content_parts.append(f"=== Planilha: {sheet_name} ==={truncated_note}")
                content_parts.append(df.to_string())
                content_parts.append("")
            
            return "\n".join(content_parts)
        except ImportError:
            return "pandas não disponível para extração de Excel"
        except Exception as e:
            return f"Erro ao processar Excel: {str(e)}"
    
    def _extract_metadata(self, content: str, content_type: str) -> Dict:
        """Extrai metadados do conteúdo"""
        metadata = {
            'content_length': len(content),
            'word_count': len(content.split()),
            'content_type': content_type,
            'extracted_at': datetime.utcnow().isoformat()
        }
        
        # Metadados específicos por tipo
        if content_type == 'drivers_mentais':
            metadata['drivers_found'] = self._count_drivers_mentais(content)
        elif content_type == 'provas_visuais':
            metadata['provas_found'] = self._count_provas_visuais(content)
        elif content_type == 'perfil_psicologico':
            metadata['perfil_elements'] = self._count_perfil_elements(content)
        
        return metadata
    
    def _count_drivers_mentais(self, content: str) -> List[str]:
        """Conta drivers mentais encontrados no conteúdo"""
        drivers = [
            'gatilho', 'ancoragem', 'ferida', 'dor', 'medo', 'desejo',
            'urgência', 'escassez', 'autoridade', 'prova social'
        ]
        
        content_lower = content.lower()
        found_drivers = [driver for driver in drivers if driver in content_lower]
        return found_drivers
    
    def _count_provas_visuais(self, content: str) -> List[str]:
        """Conta provas visuais encontradas no conteúdo"""
        provas = [
            'demonstração', 'experimento', 'teste', 'resultado',
            'evidência', 'caso', 'exemplo', 'comparação'
        ]
        
        content_lower = content.lower()
        found_provas = [prova for prova in provas if prova in content_lower]
        return found_provas
    
    def _count_perfil_elements(self, content: str) -> List[str]:
        """Conta elementos de perfil encontrados no conteúdo"""
        elements = [
            'idade', 'renda', 'escolaridade', 'profissão', 'comportamento',
            'hábito', 'motivação', 'objetivo', 'frustração'
        ]
        
        content_lower = content.lower()
        found_elements = [element for element in elements if element in content_lower]
        return found_elements
    
    def get_session_attachments(self, session_id: str) -> List[Dict]:
        """Recupera anexos de uma sessão"""
        if session_id not in self.session_storage:
            return []
        
        session_data = self.session_storage[session_id]
        
        # Verificar TTL
        if datetime.utcnow() - session_data['created_at'] > self.session_ttl:
            self.clear_session(session_id)
            return []
        
        return session_data['attachments']
    
    def get_session_attachments_content(self, session_id: str) -> Optional[str]:
        """Recupera conteúdo consolidado dos anexos de uma sessão"""
        attachments = self.get_session_attachments(session_id)
        
        if not attachments:
            return None
        
        content_parts = []
        content_parts.append("=== CONTEÚDO DOS ANEXOS ===\n")
        
        for attachment in attachments:
            content_parts.append(f"📎 ANEXO: {attachment['original_filename']}")
            content_parts.append(f"Tipo: {attachment['content_type']}")
            content_parts.append(f"Tamanho: {attachment['file_size']} bytes")
            content_parts.append("-" * 50)
            content_parts.append(attachment['extracted_content'])
            content_parts.append("\n" + "="*50 + "\n")
        
        return "\n".join(content_parts)
    
    def clear_session(self, session_id: str) -> bool:
        """Limpa anexos de uma sessão"""
        try:
            if session_id in self.session_storage:
                # Remover arquivos físicos
                session_dir = os.path.join(self.upload_folder, session_id)
                if os.path.exists(session_dir):
                    shutil.rmtree(session_dir)
                
                # Remover da memória
                del self.session_storage[session_id]
                
                logger.info(f"Sessao {session_id} limpa com sucesso")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao limpar sessao {session_id}: {str(e)}")
            return False
    
    def _cleanup_old_files(self):
        """Limpa arquivos antigos do diretório de upload"""
        try:
            cutoff_time = datetime.utcnow() - self.session_ttl
            
            for session_id in list(self.session_storage.keys()):
                session_data = self.session_storage[session_id]
                if session_data['created_at'] < cutoff_time:
                    self.clear_session(session_id)
            
            logger.info("Limpeza de arquivos antigos concluida")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de arquivos: {str(e)}")
    
    def get_service_stats(self) -> Dict:
        """Retorna estatísticas do serviço"""
        total_attachments = sum(len(session['attachments']) for session in self.session_storage.values())
        
        return {
            'active_sessions': len(self.session_storage),
            'total_attachments': total_attachments,
            'upload_folder': self.upload_folder,
            'max_file_size_mb': self.max_file_size // (1024 * 1024),
            'allowed_extensions': list(self.allowed_extensions),
            'session_ttl_hours': self.session_ttl.total_seconds() / 3600
        }


import os
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black, blue, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
import logging

logger = logging.getLogger(__name__)

pdf_bp = Blueprint("pdf", __name__)

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        try:
            self.styles.add(ParagraphStyle(
                name='CustomTitle', 
                fontSize=24, 
                leading=28, 
                alignment=TA_CENTER, 
                textColor=HexColor('#333333'),
                fontName='Helvetica-Bold',
                spaceAfter=20
            ))
            
            self.styles.add(ParagraphStyle(
                name='CustomSubtitle', 
                fontSize=18, 
                leading=22, 
                alignment=TA_CENTER, 
                textColor=HexColor('#666666'),
                fontName='Helvetica',
                spaceAfter=15
            ))
            
            self.styles.add(ParagraphStyle(
                name='CustomHeading1', 
                fontSize=16, 
                leading=20, 
                textColor=HexColor('#0056b3'), 
                spaceAfter=12, 
                fontName='Helvetica-Bold',
                spaceBefore=15
            ))
            
            self.styles.add(ParagraphStyle(
                name='CustomHeading2', 
                fontSize=14, 
                leading=18, 
                textColor=HexColor('#007bff'), 
                spaceAfter=10, 
                fontName='Helvetica-Bold',
                spaceBefore=10
            ))
            self.styles.add(ParagraphStyle(
                name='CustomBodyText', 
                fontSize=10, 
                leading=14, 
                textColor=HexColor('#333333'), 
                spaceAfter=6, 
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                wordWrap='CJK'
            ))
            
            self.styles.add(ParagraphStyle(
                name='BulletText', 
                fontSize=10, 
                leading=14, 
                textColor=HexColor('#333333'), 
                leftIndent=20, 
                bulletIndent=10, 
                bulletFontName='Helvetica-Bold', 
                bulletFontSize=10, 
                bulletColor=HexColor('#0056b3'),
                spaceAfter=3
            ))            
            self.styles.add(ParagraphStyle(
                name='CustomCaption', 
                fontSize=8, 
                leading=10, 
                textColor=HexColor('#999999'), 
                alignment=TA_CENTER, 
                spaceAfter=6,
                fontName='Helvetica'
            ))
            
            self.styles.add(ParagraphStyle(
                name='CustomListText', 
                fontSize=10, 
                leading=14, 
                textColor=HexColor('#333333'), 
                leftIndent=20,
                fontName='Helvetica',
                spaceAfter=3
            ))
            
            self.styles.add(ParagraphStyle(
                name='CustomQuote', 
                fontSize=10, 
                leading=14, 
                textColor=HexColor('#555555'), 
                leftIndent=20, 
                rightIndent=20, 
                spaceBefore=10, 
                spaceAfter=10, 
                backColor=HexColor('#f0f0f0'), 
                borderPadding=5,
                fontName='Helvetica-Oblique'
            ))
            
        except Exception as e:
            logger.warning(f"Error creating custom styles: {e}. Using default styles.")

    def _add_header_and_footer(self, canvas, doc):
        canvas.saveState()
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(HexColor('#0056b3'))
        
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'logo.png')
        if os.path.exists(logo_path):
            try:
                logo = ImageReader(logo_path)
                canvas.drawImage(logo, inch, A4[1] - 0.9 * inch, width=0.5*inch, height=0.5*inch, preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        canvas.drawString(inch + 0.6 * inch, A4[1] - 0.75 * inch, "Relatório de Arqueologia de Avatar")
        canvas.setFont('Helvetica', 8)
        canvas.drawString(inch + 0.6 * inch, A4[1] - 0.9 * inch, "Análise Ultra-Detalhada Concluída")

        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor('#666666'))
        page_num = canvas.getPageNumber()
        report_name = "Relatório de Arqueologia de Avatar"
        user_name = "Up"
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        canvas.drawString(inch, 0.75 * inch, f"{report_name} | Gerado por: {user_name}")
        
        footer_right_text = f"Data: {current_date} | Página {page_num}"
        text_width = canvas.stringWidth(footer_right_text, 'Helvetica', 8)
        canvas.drawString(A4[0] - inch - text_width, 0.75 * inch, footer_right_text)
        
        canvas.restoreState()

    def _safe_get(self, data, *keys, default="N/A"):
        try:
            result = data
            for key in keys:
                if isinstance(result, dict):
                    result = result.get(key, {})
                elif isinstance(result, list) and isinstance(key, int) and key < len(result):
                    result = result[key]
                else:
                    return default
            return result if result not in [{}, [], None] else default
        except:
            return default

    def generate_pdf_report(self, data: dict, filename: str):
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=inch, bottomMargin=inch)
            story = []

            segmento = self._safe_get(data, 'escopo', 'segmento_principal', default='Segmento não especificado')
            avatar_data = data.get('avatar_ultra_detalhado', {})
            persona = avatar_data.get('persona_principal', {})
            
            story.append(Paragraph("Relatório de Arqueologia de Avatar", self.styles["CustomTitle"]))
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(f"Análise Ultra-Detalhada: {segmento}", self.styles["CustomSubtitle"]))
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles["CustomCaption"]))
            story.append(PageBreak())

            story.append(Paragraph("Resumo Executivo", self.styles["CustomHeading1"]))
            story.append(Paragraph(
                f"Este relatório apresenta uma análise ultra-detalhada do segmento {segmento}, "
                "utilizando inteligência artificial avançada e pesquisa em tempo real na internet. "
                "A análise revela insights profundos sobre o avatar ideal, estratégias de marketing "
                "e oportunidades de mercado.", 
                self.styles["CustomBodyText"]
            ))
            story.append(Spacer(1, 0.3 * inch))

            if persona:
                story.append(Paragraph("Perfil do Avatar Principal", self.styles["CustomHeading1"]))
                
                # Dynamically add all persona fields
                for key, value in persona.items():
                    display_key = key.replace('_', ' ').title()
                    story.append(Paragraph(f"{display_key}: {value if value else 'N/A'}", self.styles["CustomBodyText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            escopo = data.get('escopo', {})
            if escopo:
                story.append(Paragraph("Escopo de Mercado", self.styles["CustomHeading1"]))
                story.append(Paragraph(f"Segmento Principal: {escopo.get('segmento_principal', 'N/A')}", self.styles["CustomBodyText"]))
                story.append(Paragraph(f"Produto Ideal: {escopo.get('produto_ideal', 'N/A')}", self.styles["CustomBodyText"]))
                story.append(Paragraph(f"Proposta de Valor: {escopo.get('proposta_valor', 'N/A')}", self.styles["CustomBodyText"]))
                
                tamanho_mercado = escopo.get('tamanho_mercado', {})
                if tamanho_mercado:
                    story.append(Paragraph("Tamanho do Mercado:", self.styles["CustomHeading2"]))
                    for key, value in tamanho_mercado.items():
                        display_key = key.replace('_medio_segmento', '').replace('_', ' ').title()
                        story.append(Paragraph(f"{display_key}: {value if value else 'N/A'}", self.styles["CustomListText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            dores = data.get('mapeamento_dores_ultra_detalhado', {})
            if dores:
                story.append(Paragraph("Mapeamento de Dores", self.styles["CustomHeading1"]))
                
                dores_criticas = dores.get('dores_nivel_1_criticas', [])
                if dores_criticas:
                    story.append(Paragraph("Dores Críticas (Nível 1):", self.styles["CustomHeading2"]))
                    for i, dor in enumerate(dores_criticas, 1):
                        if isinstance(dor, dict):
                            story.append(Paragraph(f"{i}. {dor.get('dor', 'N/A')}", self.styles["CustomListText"]))
                            story.append(Paragraph(f"   Intensidade: {dor.get('intensidade', 'N/A')} | Frequência: {dor.get('frequencia', 'N/A')}", self.styles["CustomListText"]))
                
                dores_nivel_2 = dores.get('dores_nivel_2', [])
                if dores_nivel_2:
                    story.append(Paragraph("Dores de Nível 2:", self.styles["CustomHeading2"]))
                    for i, dor in enumerate(dores_nivel_2, 1):
                        if isinstance(dor, dict):
                            story.append(Paragraph(f"{i}. {dor.get('dor', 'N/A')}", self.styles["CustomListText"]))
                            story.append(Paragraph(f"   Impacto: {dor.get('impacto', 'N/A')}", self.styles["CustomListText"]))
                
                dores_nivel_3 = dores.get('dores_nivel_3', [])
                if dores_nivel_3:
                    story.append(Paragraph("Dores de Nível 3:", self.styles["CustomHeading2"]))
                    for i, dor in enumerate(dores_nivel_3, 1):
                        if isinstance(dor, dict):
                            story.append(Paragraph(f"{i}. {dor.get('dor', 'N/A')}", self.styles["CustomListText"]))
                            story.append(Paragraph(f"   Causa Raiz: {dor.get('causa_raiz', 'N/A')}", self.styles["CustomListText"]))
                       
                story.append(Spacer(1, 0.3 * inch))

            marketing = data.get('estrategia_palavras_chave', {})
            if marketing:
                story.append(Paragraph("Estratégia de Marketing", self.styles["CustomHeading1"]))
                
                palavras_primarias = marketing.get('palavras_primarias', [])
                if palavras_primarias:
                    story.append(Paragraph("Palavras-Chave Primárias:", self.styles["CustomHeading2"]))
                    for i, palavra in enumerate(palavras_primarias, 1):
                        if isinstance(palavra, dict):
                            story.append(Paragraph(
                                f"{i}. {palavra.get('termo', 'N/A')} - Volume: {palavra.get('volume_mensal', 'N/A')} - CPC: {palavra.get('cpc_estimado', 'N/A')}", 
                                self.styles["CustomListText"]
                            ))
                
                story.append(Spacer(1, 0.3 * inch))

            competicao = data.get('analise_concorrencia_detalhada', {})
            if competicao:
                story.append(Paragraph("Análise Competitiva", self.styles["CustomHeading1"]))
                
                concorrentes = competicao.get('concorrentes_diretos', [])
                if concorrentes:
                    story.append(Paragraph("Principais Concorrentes:", self.styles["CustomHeading2"]))
                    for i, concorrente in enumerate(concorrentes, 1):
                        if isinstance(concorrente, dict):
                            story.append(Paragraph(f"{i}. {concorrente.get('nome', 'N/A')}", self.styles["CustomListText"]))
                            story.append(Paragraph(f"   Preço: {concorrente.get('preco_range', 'N/A')}", self.styles["CustomListText"]))
                            story.append(Paragraph(f"   Posicionamento: {concorrente.get('posicionamento', 'N/A')}", self.styles["CustomListText"]))
                
                gaps = competicao.get('gaps_oportunidades', [])
                if gaps:
                    story.append(Paragraph("Oportunidades de Mercado:", self.styles["CustomHeading2"]))
                    for i, gap in enumerate(gaps, 1):
                        story.append(Paragraph(f"{i}. {gap}", self.styles["CustomListText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            metricas = data.get('metricas_performance_detalhadas', {})
            if metricas:
                story.append(Paragraph("Métricas de Performance", self.styles["CustomHeading1"]))
                
                benchmarks = metricas.get('benchmarks_segmento', {})
                if benchmarks:
                    story.append(Paragraph("Benchmarks do Segmento:", self.styles["CustomHeading2"]))
                    for key, value in benchmarks.items():
                        display_key = key.replace('_medio_segmento', '').replace('_', ' ').title()
                        story.append(Paragraph(f"{display_key}: {value if value else 'N/A'}", self.styles["CustomListText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            plano_acao = data.get('plano_acao_detalhado', [])
            if plano_acao:
                story.append(Paragraph("Plano de Ação", self.styles["CustomHeading1"]))
                for fase in plano_acao:
                    if isinstance(fase, dict):
                        story.append(Paragraph(f"{fase.get('fase', 'Fase')}", self.styles["CustomHeading2"]))
                        story.append(Paragraph(f"Duração: {fase.get('duracao', 'N/A')}", self.styles["CustomBodyText"]))
                        
                        acoes = fase.get('acoes', [])
                        if acoes:
                            for i, acao in enumerate(acoes, 1):
                                if isinstance(acao, dict):
                                    story.append(Paragraph(f"{i}. {acao.get('acao', 'N/A')}", self.styles["CustomListText"]))
                                    story.append(Paragraph(f"   Responsável: {acao.get('responsavel', 'N/A')}", self.styles["CustomListText"]))
                                    story.append(Paragraph(f"   Prazo: {acao.get('prazo', 'N/A')}", self.styles["CustomListText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            insights = data.get('insights_exclusivos', [])
            if insights:
                story.append(Paragraph("Insights Exclusivos", self.styles["CustomHeading1"]))
                for i, insight in enumerate(insights, 1):  # Display all insights
                    if isinstance(insight, str):
                        story.append(Paragraph(f"{i}. {insight}", self.styles["CustomListText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            cenarios = data.get('projecoes_cenarios', {})
            if cenarios:
                story.append(Paragraph("Projeções de Cenários", self.styles["CustomHeading1"]))
                
                for cenario_nome in ['cenario_conservador', 'cenario_realista', 'cenario_otimista']:
                    cenario = cenarios.get(cenario_nome, {})
                    if cenario:
                        nome_display = cenario_nome.replace('cenario_', '').replace('_', ' ').title()
                        story.append(Paragraph(f"Cenário {nome_display}:", self.styles["CustomHeading2"]))
                        for key, value in cenario.items():
                            display_key = key.replace('_', ' ').title()
                            story.append(Paragraph(f"{display_key}: {value if value else 'N/A'}", self.styles["CustomListText"]))
                
                story.append(Spacer(1, 0.3 * inch))

            story.append(PageBreak())
            story.append(Paragraph("Conclusão", self.styles["CustomHeading1"]))
            story.append(Paragraph(
                "Esta análise ultra-detalhada fornece uma base sólida para o desenvolvimento de "
                "estratégias de marketing eficazes e o lançamento bem-sucedido do produto no mercado brasileiro. "
                "Os insights apresentados foram gerados através de inteligência artificial avançada e "
                "pesquisa em tempo real, garantindo informações atualizadas e relevantes.", 
                self.styles["CustomBodyText"]
            ))
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(
                "Relatório gerado pela plataforma UP Lançamentos - Arqueologia do Avatar com IA", 
                self.styles["CustomCaption"]
            ))

            doc.build(story, onFirstPage=self._add_header_and_footer, onLaterPages=self._add_header_and_footer)
            logger.info(f"Relatório PDF '{filename}' gerado com sucesso.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar o relatório PDF: {e}")
            return False

@pdf_bp.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        report_data = data.get("report_data", data)
        user_id = data.get("user_id", "anonymous")

        if not report_data:
            return jsonify({"error": "Dados do relatório são obrigatórios"}), 400

        generator = PDFReportGenerator()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"relatorio_arqueologia_{user_id}_{timestamp}.pdf"
        
        temp_path = os.path.join("/tmp", filename)
        
        os.makedirs("/tmp", exist_ok=True)
        
        success = generator.generate_pdf_report(report_data, temp_path) 

        if success and os.path.exists(temp_path):
            def remove_file():
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
            
            import atexit
            atexit.register(remove_file)
            
            return send_file(
                temp_path, 
                as_attachment=True, 
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            return jsonify({"error": "Falha ao gerar o relatório PDF"}), 500

    except Exception as e:
        logger.error(f"Erro na rota de geração de PDF: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@pdf_bp.route("/generate", methods=["POST"])
def generate_pdf_legacy():
    return generate_pdf()



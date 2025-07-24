# Arquitetura e Funcionalidades do arqv30_enhanced

## Arquitetura

O aplicativo `arqv30_enhanced` é desenvolvido utilizando o microframework Flask, seguindo uma abordagem modular para organização do código. A estrutura é composta por:

- **Flask**: Atua como o core do aplicativo web, gerenciando as requisições HTTP e as respostas.
- **Flask-CORS**: Essencial para permitir que o frontend (que pode estar em um domínio diferente) se comunique com o backend, lidando com as políticas de Cross-Origin Resource Sharing.
- **python-dotenv**: Utilizado para carregar variáveis de ambiente de um arquivo `.env`, garantindo que informações sensíveis como chaves de API e URLs de banco de dados não sejam expostas diretamente no código-fonte.
- **SQLAlchemy**: É a ORM (Object-Relational Mapper) utilizada para interagir com o banco de dados. O `main.py` indica uma configuração otimizada para o Supabase, sugerindo que o Supabase é o provedor de banco de dados preferencial.
- **Blueprints**: As funcionalidades são organizadas em Blueprints do Flask, como `user_bp` (para rotas relacionadas a usuários) e `analysis_bp` (para rotas de análise de mercado). Isso promove a modularidade e a manutenibilidade do código.
- **Camada de Serviços (`services/`)**: Uma camada crucial que abstrai a lógica de negócio complexa e a integração com serviços externos. Inclui:
    - `GeminiClient`: Responsável pela comunicação com a API do Google Gemini Pro 2.5 para geração de análises detalhadas.
    - `DeepSearchService`: Gerencia a pesquisa profunda na internet, atuando como um fallback para o WebSailor.
    - `AttachmentService`: Lida com o upload, processamento e recuperação de anexos (arquivos) que podem ser usados como contexto para as análises.
    - `WebSailorIntegrationService`: Integração com o serviço WebSailor para pesquisa web avançada e verificação de fatos, sendo a opção preferencial para busca profunda.

## Funcionalidades Principais

O `arqv30_enhanced` é uma ferramenta robusta para análise de mercado e inteligência de negócios, com foco em geração de insights detalhados. Suas principais funcionalidades incluem:

1.  **Análise Ultra-Detalhada de Mercado (`/api/analyze`)**:
    -   Recebe dados de entrada como segmento, produto, público-alvo, preço, concorrentes, dados adicionais, objetivos de receita, orçamento de marketing e prazo de lançamento.
    -   Utiliza o Google Gemini Pro 2.5 para gerar uma análise abrangente, incluindo perfil de avatar (demográfico e psicográfico), dores, desejos, gatilhos mentais, posicionamento de mercado, análise de concorrência, estratégia de palavras-chave, métricas de performance, projeções de cenários, inteligência de mercado e um plano de ação detalhado.
    -   Incorpora contexto de pesquisa profunda na internet (via WebSailor ou DeepSearch) e conteúdo de anexos para enriquecer a análise.
    -   Persiste os resultados da análise no Supabase.

2.  **Upload e Processamento de Anexos (`/api/upload_attachment`)**:
    -   Permite o upload de arquivos (anexos) que são associados a uma sessão específica.
    -   O conteúdo desses anexos é processado e pode ser utilizado como contexto adicional nas análises do Gemini.

3.  **Busca Profunda na Internet (`/api/deep_search` e `/api/websailor_research`)**:
    -   Realiza pesquisas web avançadas para coletar informações relevantes que complementam os dados fornecidos pelo usuário.
    -   Prioriza o uso do WebSailor para pesquisa, com o DeepSearch como fallback.
    -   Inclui endpoints específicos para verificação de fatos (`/api/fact_check`) e pesquisa de mercado (`/api/market_research`) utilizando o WebSailor.

4.  **Análise em Lote (`/api/analyze_batch`)**:
    -   Permite o processamento de múltiplas análises de mercado simultaneamente.
    -   Cada item do lote pode incluir sua própria query de pesquisa e anexos, sendo processado de forma independente.

5.  **Geração de Relatórios em PDF (`/api/generate_pdf`)**:
    -   Converte o resultado da análise detalhada em um relatório PDF formatado, facilitando a visualização e o compartilhamento.

6.  **Gerenciamento de Análises e Segmentos (`/api/analyses`, `/api/analyses/<id>`, `/api/segmentos`)**:
    -   Fornece rotas para listar análises recentes, buscar análises por ID e obter uma lista de segmentos únicos analisados.
    -   Mantém compatibilidade com o termo 


-- Fix missing columns in analyses table
-- This migration adds any missing columns that the application expects

DO $$
BEGIN
    -- Add objetivo_receita if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'analyses' AND column_name = 'objetivo_receita'
    ) THEN
        ALTER TABLE analyses ADD COLUMN objetivo_receita DECIMAL(15,2);
        RAISE NOTICE 'Added objetivo_receita column';
    END IF;

    -- Add orcamento_marketing if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'analyses' AND column_name = 'orcamento_marketing'
    ) THEN
        ALTER TABLE analyses ADD COLUMN orcamento_marketing DECIMAL(15,2);
        RAISE NOTICE 'Added orcamento_marketing column';
    END IF;

    -- Add prazo_lancamento if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'analyses' AND column_name = 'prazo_lancamento'
    ) THEN
        ALTER TABLE analyses ADD COLUMN prazo_lancamento VARCHAR(100);
        RAISE NOTICE 'Added prazo_lancamento column';
    END IF;

    -- Add comprehensive_analysis if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'analyses' AND column_name = 'comprehensive_analysis'
    ) THEN
        ALTER TABLE analyses ADD COLUMN comprehensive_analysis JSONB;
        RAISE NOTICE 'Added comprehensive_analysis column';
    END IF;

    -- Add market_intelligence if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'analyses' AND column_name = 'market_intelligence'
    ) THEN
        ALTER TABLE analyses ADD COLUMN market_intelligence JSONB;
        RAISE NOTICE 'Added market_intelligence column';
    END IF;

    -- Add action_plan if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'analyses' AND column_name = 'action_plan'
    ) THEN
        ALTER TABLE analyses ADD COLUMN action_plan JSONB;
        RAISE NOTICE 'Added action_plan column';
    END IF;
END $$;

-- Create indexes for new columns if they don't exist
CREATE INDEX IF NOT EXISTS idx_analyses_comprehensive_analysis 
ON analyses USING GIN (comprehensive_analysis);

CREATE INDEX IF NOT EXISTS idx_analyses_market_intelligence 
ON analyses USING GIN (market_intelligence);

CREATE INDEX IF NOT EXISTS idx_analyses_action_plan 
ON analyses USING GIN (action_plan);

-- Add comments for documentation
COMMENT ON COLUMN analyses.objetivo_receita IS 'Meta de receita para o lançamento do produto/serviço';
COMMENT ON COLUMN analyses.orcamento_marketing IS 'Orçamento disponível para investimento em marketing';
COMMENT ON COLUMN analyses.prazo_lancamento IS 'Prazo desejado para o lançamento do produto/serviço';
COMMENT ON COLUMN analyses.comprehensive_analysis IS 'Análise completa e ultra-detalhada gerada pelo Gemini Pro';
COMMENT ON COLUMN analyses.market_intelligence IS 'Dados de inteligência de mercado coletados via pesquisa na internet';
COMMENT ON COLUMN analyses.action_plan IS 'Plano de ação detalhado com fases e métricas de sucesso';
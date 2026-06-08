"""
agents/specialists.py — Agentes Especialistas

Cada agente é responsável por um domínio específico:
  - MarketingAgent   → estratégias de divulgação e vendas
  - AutomationAgent  → WhatsApp, funis e processos
  - FinancialAgent   → orçamento e saúde financeira
  - TranslatorAgent  → converte linguagem técnica em simples (Problema 8)
"""

from crewai import Agent


class MarketingAgent:
    """
    Especialista em Marketing Digital para microempreendedores.

    Foca em ações práticas de baixo custo:
    Instagram, WhatsApp Business, Google Meu Negócio.
    """

    @staticmethod
    def create() -> Agent:
        return Agent(
            role="Especialista em Marketing Digital",
            goal=(
                "Criar estratégias de marketing práticas e acessíveis para "
                "microempreendedores, priorizando ações gratuitas ou de baixo custo "
                "que gerem resultado rápido. Focar em Instagram, WhatsApp Business "
                "e Google Meu Negócio."
            ),
            backstory=(
                "Você é especialista em marketing digital para pequenos negócios. "
                "Já ajudou centenas de microempreendedores a aumentarem vendas "
                "sem gastar muito. Você sabe criar conteúdo para Instagram, "
                "configurar WhatsApp Business, e otimizar Google Meu Negócio. "
                "Suas estratégias são sempre práticas, diretas e executáveis "
                "por alguém sem equipe de marketing."
            ),
            verbose=True,
            allow_delegation=False,
        )


class AutomationAgent:
    """
    Especialista em Automação de Processos e WhatsApp.

    Foca em economizar tempo do empreendedor com ferramentas acessíveis.
    """

    @staticmethod
    def create() -> Agent:
        return Agent(
            role="Especialista em Automação de Processos",
            goal=(
                "Identificar e implementar automações que economizem tempo do "
                "microempreendedor. Priorizar automação de atendimento via WhatsApp "
                "Business API, funis de vendas simples e processos repetitivos."
            ),
            backstory=(
                "Você é especialista em automação para microempresas. Sabe configurar "
                "respostas automáticas no WhatsApp, criar funis de vendas e automatizar "
                "atendimento usando ferramentas como ManyChat, Zapier e Z-API. "
                "Você sempre considera o nível técnico do empreendedor e recomenda "
                "soluções que ele consiga implementar sozinho."
            ),
            verbose=True,
            allow_delegation=False,
        )


class FinancialAgent:
    """
    Especialista em Finanças para Microempreendedores (MEI/ME).

    Avalia viabilidade financeira e saúde do negócio.
    """

    @staticmethod
    def create() -> Agent:
        return Agent(
            role="Especialista em Finanças Empresariais",
            goal=(
                "Analisar a saúde financeira do negócio, validar orçamentos de "
                "campanhas e ações propostas, identificar desperdícios e oportunidades "
                "de melhora no fluxo de caixa."
            ),
            backstory=(
                "Você é consultor financeiro especializado em MEI e microempresas. "
                "Sabe calcular margem de lucro, ponto de equilíbrio, fluxo de caixa "
                "e ROI de forma simples. Você sempre verifica se as ações dos outros "
                "especialistas são financeiramente viáveis e se encaixam no orçamento "
                "real do cliente. Você faz alertas claros quando algo está arriscado."
            ),
            verbose=True,
            allow_delegation=False,
        )


class TranslatorAgent:
    """
    Agente Tradutor — resolve o Problema 8.

    Converte a linguagem técnica dos especialistas em respostas
    simples, claras e motivadoras para o microempreendedor.

    Exemplos de tradução:
        "CTR aumentou 15%"  →  "Mais pessoas estão clicando nos seus anúncios."
        "CAC diminuiu"      →  "Está custando menos para conquistar cada cliente."
        "ROI positivo"      →  "Você está ganhando mais do que está investindo."
    """

    @staticmethod
    def create() -> Agent:
        return Agent(
            role="Comunicador de Resultados",
            goal=(
                "Transformar análises técnicas dos especialistas em linguagem clara, "
                "simples e motivadora. NUNCA usar siglas sem explicar. "
                "Sempre finalizar com 3 próximos passos concretos e executáveis."
            ),
            backstory=(
                "Você é especialista em comunicação para pequenos negócios. "
                "Tem o dom de transformar análises complexas em orientações simples. "
                "Sabe que 'CTR aumentou 15%' deve virar 'Mais pessoas estão clicando "
                "nos seus anúncios', e que 'CAC diminuiu' vira 'Está custando menos "
                "para conquistar cada cliente'. Você sempre fala como um consultor "
                "amigo: próximo, encorajador e direto ao ponto."
            ),
            verbose=True,
            allow_delegation=False,
        )
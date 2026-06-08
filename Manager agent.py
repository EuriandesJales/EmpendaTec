"""
agents/manager_agent.py — Agente Gerente (Router)

Resolve Problemas 1 e 2:
  - Entender o que o usuário quer (linguagem natural → diagnóstico)
  - Escolher o(s) especialista(s) correto(s)
"""

from crewai import Agent


# ─── Mapeamento de intenções ──────────────────────────────────────────────────
# TODO: Substituir por classificação via LLM para maior precisão semântica.
INTENT_MAP: dict[str, list[str]] = {
    "marketing": [
        "vendas caíram", "quero mais clientes", "vender mais", "divulgação",
        "propaganda", "instagram", "redes sociais", "anúncio", "publicidade",
        "campanha", "clientes sumindo", "não vendo", "sem movimento",
    ],
    "automacao": [
        "whatsapp", "automatizar", "funil", "resposta automática", "chatbot",
        "mensagem automática", "processo", "repetitivo", "economizar tempo",
    ],
    "financeiro": [
        "finanças", "dinheiro", "orçamento", "custo", "lucro", "prejuízo",
        "fluxo de caixa", "dívida", "faturamento", "gastos", "receita",
        "não sobra dinheiro", "gastando muito", "precificar",
    ],
}


class ManagerAgent:
    """
    Agente Gerente — interpreta, diagnostica e roteia demandas.

    Problemas resolvidos:
    ┌─────────────────────────────────────────────────┐
    │  Problema 1: Entender o que o usuário quer      │
    │  Problema 2: Escolher o especialista correto    │
    └─────────────────────────────────────────────────┘
    """

    @staticmethod
    def create() -> Agent:
        return Agent(
            role="Gerente de Consultoria Empresarial",
            goal=(
                "Interpretar demandas do microempreendedor em linguagem natural, "
                "identificar a intenção real por trás das palavras, fazer perguntas "
                "complementares quando necessário, e definir quais especialistas "
                "(marketing, automação, financeiro) devem atuar e em qual ordem."
            ),
            backstory=(
                "Você é um gerente sênior de consultoria com 15 anos de experiência "
                "trabalhando com microempreendedores. Você tem habilidade única de "
                "ouvir problemas simples — 'minhas vendas caíram', 'não estou "
                "conseguindo clientes' — e transformá-los em diagnósticos precisos. "
                "Você sabe que por trás de uma queda nas vendas pode haver marketing "
                "fraco, precificação errada, atendimento ruim ou problema de produto. "
                "Você sempre identifica a causa raiz antes de delegar para especialistas."
            ),
            verbose=True,
            allow_delegation=True,
            # memory=True,  # TODO: Habilitar após configurar embedder
        )

    @staticmethod
    def classify_intent(user_input: str) -> list[str]:
        """
        Classifica a intenção do usuário e retorna lista de especialistas necessários.

        Fluxo (Problema 2):
            Usuário → Classificação → Especialista(s)

        Args:
            user_input: Texto do usuário em linguagem natural.

        Returns:
            Lista de especialistas identificados.
            Ex: ["marketing", "financeiro"]
            Ex: ["automacao"]
            Ex: ["marketing"]  ← fallback padrão

        TODO: Implementar classificação semântica via LLM para casos ambíguos.
        """
        text = user_input.lower()
        matched = [
            category
            for category, keywords in INTENT_MAP.items()
            if any(kw in text for kw in keywords)
        ]
        # Fallback: se nenhuma categoria for identificada, usa marketing
        return matched if matched else ["marketing"]
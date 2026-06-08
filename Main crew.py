"""
crews/main_crew.py — Orquestração Principal com CrewAI

Resolve Problemas 3 e 9:
  - Problema 3: Comunicação entre agentes (contexto compartilhado via task.context)
  - Problema 9: Coordenação de múltiplos especialistas em sequência

Fluxo:
    Gerente → Classificação → Especialistas(s) → Tradutor → Resposta
"""

from crewai import Crew, Task, Process

from agents.manager_agent import ManagerAgent
from agents.specialists import (
    AutomationAgent,
    FinancialAgent,
    MarketingAgent,
    TranslatorAgent,
)


class ConsultorCrew:
    """
    Crew principal que orquestra o fluxo completo de consultoria.

    Arquitetura sequencial:
    ┌──────────┐    ┌────────────┐    ┌──────────────┐    ┌───────────┐
    │  Gerente │ →  │ Especia-   │ →  │  Financeiro  │ →  │ Tradutor  │
    │ (router) │    │ listas(s)  │    │  (validação) │    │ (saída)   │
    └──────────┘    └────────────┘    └──────────────┘    └───────────┘
    """

    def __init__(self, user_input: str, context: str = "", project_id: str = None):
        self.user_input = user_input
        self.context = context or "Nenhum histórico anterior disponível."
        self.project_id = project_id

        # Instancia agentes
        self.manager = ManagerAgent.create()
        self.marketing = MarketingAgent.create()
        self.automation = AutomationAgent.create()
        self.financial = FinancialAgent.create()
        self.translator = TranslatorAgent.create()

        # Identifica especialistas necessários (Problema 2)
        self.needed = ManagerAgent.classify_intent(user_input)

    # ─── Construtores de Tasks ────────────────────────────────────────────────

    def _task_manager(self) -> Task:
        """Problema 1: Diagnostica a demanda e define quais especialistas atuar."""
        return Task(
            description=f"""
Analise a seguinte demanda do microempreendedor:

"{self.user_input}"

Contexto de conversas anteriores:
{self.context}

Sua análise deve:
1. Identificar o problema REAL por trás das palavras do usuário
2. Determinar a causa raiz (marketing, automação, financeiro ou combinação)
3. Listar os especialistas necessários e a ordem de atuação
4. Definir o objetivo principal desta consultoria
5. Levantar perguntas complementares relevantes (se a demanda for vaga)
            """,
            expected_output="""
Diagnóstico estruturado contendo:
- Problema identificado (em linguagem clara, sem jargões)
- Causa(s) raiz identificada(s)
- Especialistas necessários e por quê cada um
- Objetivo principal da consultoria
- Perguntas complementares (se necessário)
            """,
            agent=self.manager,
        )

    def _task_marketing(self, manager_task: Task) -> Task:
        """Estratégia de marketing prática para o microempreendedor."""
        return Task(
            description=f"""
Com base no diagnóstico do Gerente, crie uma estratégia de marketing para:
"{self.user_input}"

Regras:
- Priorizar ações GRATUITAS ou de baixo custo (até R$200)
- O empreendedor não tem equipe — as ações devem ser executáveis por ele mesmo
- Focar em canais: Instagram, WhatsApp Business, Google Meu Negócio
- Ações concretas para os próximos 7 dias
            """,
            expected_output="""
Estratégia de marketing com:
- 3 ações prioritárias para os próximos 7 dias (numeradas)
- Canal e ferramenta recomendada para cada ação
- Resultado esperado em termos simples
- Como medir se está funcionando (métricas simples)
            """,
            agent=self.marketing,
            context=[manager_task],  # Problema 3: compartilha contexto do gerente
        )

    def _task_automation(self, manager_task: Task) -> Task:
        """Automações de processo e atendimento."""
        return Task(
            description=f"""
Com base no diagnóstico do Gerente, identifique automações para:
"{self.user_input}"

Foque em:
- Automação de atendimento via WhatsApp (respostas automáticas, catálogo)
- Funil de vendas simples (captação → nutrição → conversão)
- Processos repetitivos que consomem tempo do empreendedor
- Ferramentas gratuitas ou de baixo custo
            """,
            expected_output="""
Plano de automação com:
- 2-3 automações prioritárias (numeradas)
- Ferramenta sugerida e custo mensal
- Passo a passo de implementação simplificado
- Tempo estimado para implementar cada uma
            """,
            agent=self.automation,
            context=[manager_task],
        )

    def _task_financial(self, manager_task: Task, specialist_tasks: list[Task]) -> Task:
        """Valida viabilidade financeira das ações propostas."""
        return Task(
            description=f"""
Com base no diagnóstico e nas estratégias dos especialistas, valide os aspectos
financeiros para a demanda: "{self.user_input}"

Avalie:
- Investimento mínimo necessário para cada ação proposta
- Retorno esperado (prazo e valor estimado)
- Riscos financeiros que o empreendedor deve conhecer
- Se o investimento é viável para um microempreendedor
            """,
            expected_output="""
Análise financeira com:
- Investimento total mínimo necessário (R$)
- Retorno esperado (em quanto tempo e quanto)
- Top 2 riscos financeiros
- Recomendação de orçamento por ação
- Sinal verde ou alerta para cada estratégia proposta
            """,
            agent=self.financial,
            context=[manager_task] + specialist_tasks,  # Problema 3: contexto completo
        )

    def _task_translator(self, all_tasks: list[Task]) -> Task:
        """Problema 8: Traduz linguagem técnica para o microempreendedor."""
        return Task(
            description=f"""
Pegue TODOS os resultados dos especialistas e crie UMA resposta final clara e
motivadora para o microempreendedor.

A demanda original foi: "{self.user_input}"

REGRAS OBRIGATÓRIAS:
- ZERO termos técnicos sem explicação imediata
- Tom amigável, encorajador e próximo
- Máximo 3 próximos passos — concretos e práticos
- Começar reconhecendo o problema do usuário
- Terminar com uma mensagem de encorajamento

FORMATO DA RESPOSTA:
Parte 1 (para o usuário): resposta simplificada
Parte 2 (log interno): resumo técnico, métricas e especialistas que atuaram
            """,
            expected_output="""
RESPOSTA FINAL (para o usuário):
- Parágrafo de reconhecimento do problema
- O que foi descoberto (linguagem do dia a dia)
- Os 3 próximos passos (numerados e práticos)
- Mensagem de encorajamento final

RESUMO TÉCNICO (para log interno):
- Especialistas que atuaram
- Principais métricas definidas
- Objetivos identificados
            """,
            agent=self.translator,
            context=all_tasks,  # Problema 3: vê tudo que foi produzido
        )

    # ─── Execução ─────────────────────────────────────────────────────────────

    def run(self) -> dict:
        """
        Executa o fluxo completo de consultoria.

        Problema 9: Coordena múltiplos especialistas de forma orquestrada.

        Returns:
            dict com:
              - simplified: resposta em linguagem simples (para o usuário)
              - technical:  análise técnica completa (para log)
              - specialists_used: lista de especialistas que atuaram
              - metadata: informações do projeto
        """
        # 1. Gerente diagnostica e classifica
        manager_task = self._task_manager()
        tasks = [manager_task]
        specialist_tasks = []

        # 2. Adiciona tarefas dos especialistas conforme classificação
        if "marketing" in self.needed:
            t = self._task_marketing(manager_task)
            tasks.append(t)
            specialist_tasks.append(t)

        if "automacao" in self.needed:
            t = self._task_automation(manager_task)
            tasks.append(t)
            specialist_tasks.append(t)

        if "financeiro" in self.needed:
            t = self._task_financial(manager_task, specialist_tasks)
            tasks.append(t)
            # financeiro não entra em specialist_tasks para o tradutor (já é validação)

        # 3. Tradutor sempre encerra (Problema 8)
        translator_task = self._task_translator([manager_task] + specialist_tasks)
        tasks.append(translator_task)

        # 4. Monta e executa a Crew
        crew = Crew(
            agents=[
                self.manager,
                self.marketing,
                self.automation,
                self.financial,
                self.translator,
            ],
            tasks=tasks,
            process=Process.sequential,   # Sequencial garante a ordem correta
            verbose=True,
            # ── Habilitar para memória compartilhada entre agentes (Problema 3) ──
            # memory=True,
            # embedder={
            #     "provider": "openai",
            #     "config": {"model": "text-embedding-3-small"},
            # },
        )

        result = crew.kickoff()

        return self._parse_result(result)

    def _parse_result(self, crew_result) -> dict:
        """
        Transforma o resultado bruto da Crew no formato padronizado.

        TODO: Implementar parser mais sofisticado para separar as seções
              'RESPOSTA FINAL' e 'RESUMO TÉCNICO' do output do tradutor.
        """
        raw = str(crew_result)

        # Separação simples: busca pela seção técnica
        # TODO: Usar regex ou structured output para separar as partes
        if "RESUMO TÉCNICO" in raw:
            parts = raw.split("RESUMO TÉCNICO")
            simplified = parts[0].replace("RESPOSTA FINAL", "").strip()
            technical = parts[1].strip() if len(parts) > 1 else raw
        else:
            simplified = raw
            technical = raw

        return {
            "simplified": simplified,
            "technical": technical,
            "specialists_used": self.needed,
            "metadata": {
                "project_id": self.project_id,
                "intent_categories": self.needed,
                "tasks_executed": len(self.needed) + 2,  # + gerente + tradutor
            },
            # new_goal é populado se o gerente identificar um objetivo claro
            # TODO: Extrair objetivo do output do gerente e definir aqui
            "new_goal": None,
        }
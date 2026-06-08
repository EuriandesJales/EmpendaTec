"""
main.py — Ponto de entrada do Consultor IA
Execute com: uv run streamlit run main.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─── Guarda redes antes de importar os módulos que usam LLM ──────────────────
if not os.getenv("OPENAI_API_KEY"):
    st.set_page_config(page_title="Consultor IA", page_icon="🧠")
    st.error("⚠️ **OPENAI_API_KEY não configurada.**")
    st.info("Copie `.env.example` para `.env` e adicione sua chave da OpenAI.")
    st.stop()

from crews.main_crew import ConsultorCrew          # noqa: E402
from memory.memory_manager import MemoryManager    # noqa: E402
from logs.action_logger import ActionLogger        # noqa: E402
from utils.goal_tracker import GoalTracker         # noqa: E402

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Consultor IA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    .stProgress > div > div { background-color: #4CAF50; }
</style>
""", unsafe_allow_html=True)


# ─── Estado da sessão ─────────────────────────────────────────────────────────
def init_session():
    """Inicializa variáveis da sessão Streamlit (memória de curto prazo)."""
    defaults = {
        "messages": [],           # histórico do chat atual
        "project_id": "default",  # projeto ativo
        "memory": MemoryManager(),
        "logger": ActionLogger(),
        "goals": GoalTracker(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.title("🧠 Consultor IA")
        st.caption("Inteligência artificial para o seu negócio")
        st.divider()

        # Projeto ativo
        st.subheader("📁 Projeto")
        project_name = st.text_input("Nome do projeto", value="Meu Negócio")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 Novo", use_container_width=True):
                st.session_state.project_id = project_name.lower().replace(" ", "_")
                st.session_state.messages = []
                st.rerun()
        with col2:
            st.button("📂 Histórico", use_container_width=True)  # TODO

        st.caption(f"Projeto atual: `{st.session_state.project_id}`")
        st.divider()

        # Objetivos ativos (Problema 10)
        st.subheader("🎯 Objetivos Ativos")
        active_goals = st.session_state.goals.get_active_goals()
        if active_goals:
            for goal in active_goals:
                st.progress(
                    goal["progress"] / 100,
                    text=goal["description"][:45] + "…",
                )
        else:
            st.caption("Nenhum objetivo definido ainda.")

        st.divider()

        # Especialistas disponíveis
        st.subheader("👥 Especialistas")
        specialists = {
            "📢 Marketing": "Estratégias de divulgação e vendas",
            "🤖 Automação": "WhatsApp, funis e processos",
            "💰 Financeiro": "Orçamento e saúde financeira",
        }
        for name, desc in specialists.items():
            st.markdown(f"**{name}**  \n{desc}")

        st.divider()

        # Logs recentes (Problema 6)
        if st.button("📋 Logs recentes", use_container_width=True):
            logs = st.session_state.logger.get_recent_logs(limit=5)
            if logs:
                for log in logs:
                    st.json(log, expanded=False)
            else:
                st.caption("Sem logs ainda.")


# ─── Interface de chat ────────────────────────────────────────────────────────
def chat():
    st.title("💬 Fale com seu Consultor")
    st.caption("Descreva seu problema em linguagem simples — sem jargões técnicos.")

    # Exibe histórico de mensagens
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("details"):
                with st.expander("🔍 Ver análise técnica"):
                    st.json(msg["details"], expanded=False)

    # Input do usuário
    if prompt := st.chat_input("Ex: Minhas vendas caíram. O que faço?"):
        # Registra mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Processa e exibe resposta do assistente
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            with st.spinner("🤔 Analisando sua situação..."):
                response = process_input(prompt)

            status_placeholder.empty()
            st.markdown(response["simplified"])

            if response.get("details"):
                with st.expander("🔍 Análise técnica completa"):
                    st.json(response["details"], expanded=False)

        # Salva no histórico
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["simplified"],
            "details": response.get("details"),
        })


# ─── Processamento central ────────────────────────────────────────────────────
def process_input(user_input: str) -> dict:
    """
    Orquestra o fluxo completo:

    Entrada → RAG (contexto) → CrewAI → Log → Memória → Saída simplificada
    """
    mem: MemoryManager = st.session_state.memory
    log: ActionLogger = st.session_state.logger
    goals: GoalTracker = st.session_state.goals
    pid: str = st.session_state.project_id

    # 1. Recupera contexto relevante — Problema 5 (RAG)
    context = mem.retrieve_context(user_input)

    # 2. Executa a crew de agentes — Problemas 1, 2, 3, 8, 9
    try:
        crew = ConsultorCrew(
            user_input=user_input,
            context=context,
            project_id=pid,
        )
        result = crew.run()

    except Exception as e:
        log.log_error(agent="sistema", error_message=str(e))
        return {
            "simplified": f"❌ Erro ao processar sua solicitação: {e}\n\nVerifique sua chave de API e tente novamente.",
            "details": {"error": str(e)},
        }

    # 3. Registra ação — Problema 6
    log.log_action(
        agent="sistema",
        action="processou_solicitacao",
        project_id=pid,
        details={
            "input": user_input,
            "specialists_used": result.get("specialists_used", []),
        },
    )

    # 4. Atualiza memória persistente — Problema 4
    mem.save_interaction(
        user_input=user_input,
        response=result.get("technical", ""),
        metadata={"project_id": pid},
    )

    # 5. Cria objetivo se a crew identificou um — Problema 10
    if result.get("new_goal"):
        goals.add_goal(**result["new_goal"])

    return result


# ─── Entry point ─────────────────────────────────────────────────────────────
def main():
    init_session()
    sidebar()
    chat()


if __name__ == "__main__":
    main()
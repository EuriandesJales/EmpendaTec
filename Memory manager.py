"""
memory/memory_manager.py — Sistema de Memória Multi-Camada

Resolve Problemas 4 e 5:
  - Problema 4: Perda de contexto após muitas conversas
  - Problema 5: Recuperar apenas informações relevantes (RAG)

Três camadas:
  ┌─────────────────────────────────────────────────────────┐
  │  Curto prazo   → Conversa atual (lista em memória)      │
  │  Médio prazo   → Projeto em andamento (JSON no disco)   │
  │  Longo prazo   → Histórico completo (ChromaDB/RAG)      │
  └─────────────────────────────────────────────────────────┘
"""

import json
import os
from datetime import datetime
from pathlib import Path

from rag.rag_engine import RAGEngine


class MemoryManager:
    """
    Gerencia as três camadas de memória do sistema.

    Fluxo de recuperação (Problema 5):
        Nova solicitação
             ↓
        Busca de contexto (RAG)
             ↓
        Recupera trechos relevantes
             ↓
        Entrega ao agente
    """

    # Máximo de mensagens mantidas no curto prazo (evita tokens excessivos)
    SHORT_TERM_LIMIT = 10

    def __init__(self, memory_dir: str = None):
        self.memory_dir = Path(memory_dir or os.getenv("MEMORY_DIR", "./data/memory"))
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Curto prazo: lista em memória RAM (reinicia a cada sessão)
        self._short_term: list[dict] = []

        # Longo prazo: motor RAG com ChromaDB
        self.rag = RAGEngine()

    # ─── Curto Prazo ─────────────────────────────────────────────────────────

    def add_to_short_term(self, role: str, content: str):
        """
        Adiciona uma mensagem à memória de curto prazo.

        Mantém apenas as últimas SHORT_TERM_LIMIT mensagens para
        não ultrapassar o limite de contexto do LLM.
        """
        self._short_term.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        # Janela deslizante: remove as mais antigas
        if len(self._short_term) > self.SHORT_TERM_LIMIT:
            self._short_term = self._short_term[-self.SHORT_TERM_LIMIT:]

    def get_short_term(self) -> list[dict]:
        """Retorna o histórico da conversa atual (sem timestamps)."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self._short_term
        ]

    def clear_short_term(self):
        """Limpa a memória de curto prazo (novo projeto/sessão)."""
        self._short_term = []

    # ─── Médio Prazo ─────────────────────────────────────────────────────────

    def save_project(self, project_id: str, data: dict):
        """
        Persiste o estado atual do projeto em disco (JSON).

        Estrutura do projeto (Problema 3 — contexto compartilhado):
        {
            "historico":  [...],  ← interações passadas
            "decisoes":   [...],  ← decisões tomadas pelos agentes
            "tarefas":    [...],  ← tarefas concluídas e pendentes
            "objetivos":  [...],  ← metas do empreendedor
            "resultados": [...]   ← resultados observados
        }
        """
        project_file = self.memory_dir / f"project_{project_id}.json"
        existing = self.load_project(project_id)

        # Merge: atualiza campos existentes sem apagar os anteriores
        for key, value in data.items():
            if isinstance(value, list) and isinstance(existing.get(key), list):
                existing[key].extend(value)
            else:
                existing[key] = value

        existing["updated_at"] = datetime.now().isoformat()

        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    def load_project(self, project_id: str) -> dict:
        """Carrega o estado do projeto. Cria estrutura vazia se não existir."""
        project_file = self.memory_dir / f"project_{project_id}.json"

        if not project_file.exists():
            return {
                "id": project_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "historico": [],
                "decisoes": [],
                "tarefas": [],
                "objetivos": [],
                "resultados": [],
            }

        with open(project_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # ─── Longo Prazo (RAG) ───────────────────────────────────────────────────

    def save_interaction(
        self,
        user_input: str,
        response: str,
        metadata: dict = None,
    ):
        """
        Vetoriza e salva uma interação completa no ChromaDB.

        Problema 5: o histórico é salvo vetorizado para busca semântica futura.
        Problema 4: garante que o contexto não se perca entre sessões.
        """
        document = f"Usuário perguntou: {user_input}\nResposta do consultor: {response}"

        self.rag.add_document(
            content=document,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "type": "interaction",
                **(metadata or {}),
            },
        )

        # Também atualiza o curto prazo da sessão atual
        self.add_to_short_term("user", user_input)
        self.add_to_short_term("assistant", response[:500])  # Trunca para economizar tokens

    def retrieve_context(self, query: str, n_results: int = 3) -> str:
        """
        Problema 5: RAG — Recupera trechos relevantes do histórico sem
        enviar tudo para o LLM (evita custo excessivo e lentidão).

        Fluxo:
            query → embedding → busca semântica → trechos relevantes

        Args:
            query:     Demanda atual do usuário.
            n_results: Número máximo de contextos a recuperar.

        Returns:
            String com os trechos mais relevantes do histórico, prontos
            para serem injetados no prompt dos agentes.
        """
        results = self.rag.search(query, n_results=n_results)

        if not results:
            return ""

        parts = [
            f"[Histórico {i + 1}]: {r['content']}"
            for i, r in enumerate(results)
        ]
        return "\n\n".join(parts)

    def get_stats(self) -> dict:
        """Retorna estatísticas das camadas de memória."""
        return {
            "short_term_messages": len(self._short_term),
            "short_term_limit": self.SHORT_TERM_LIMIT,
            "long_term": self.rag.get_stats(),
        }
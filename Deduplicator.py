"""
utils/deduplicator.py — Deduplicação de Tarefas

Resolve Problema 7:
  Evitar que agentes repitam tarefas que já foram realizadas.

Fluxo:
  Nova tarefa
       ↓
  Consultar cache
       ↓
  Já existe?
    ├─ Sim → Reutilizar resultado anterior
    └─ Não → Executar e registrar no cache
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path


class TaskDeduplicator:
    """
    Verifica se uma tarefa já foi executada antes de rodar novamente.

    Usa MD5 da descrição da tarefa como fingerprint.
    Cache persiste entre sessões em disco (JSON).

    Problema 7 — Fluxo:
    ┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
    │  Nova tarefa│ →   │ Consultar cache  │ →   │ Já existe?     │
    └─────────────┘     └──────────────────┘     │ Sim → reusa    │
                                                  │ Não → executa  │
                                                  └────────────────┘
    """

    # Validade padrão do cache (tarefas expiram após N dias)
    DEFAULT_TTL_DAYS = 7

    def __init__(self, storage_dir: str = "./data/memory"):
        self.cache_path = Path(storage_dir) / "task_cache.json"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict = self._load()

    # ─── Persistência ─────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if not self.cache_path.exists():
            return {}
        with open(self.cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    # ─── Fingerprint ──────────────────────────────────────────────────────────

    def _fingerprint(self, task: str, context: str = "") -> str:
        """
        Gera um hash MD5 que identifica unicamente uma tarefa.

        Combina a descrição da tarefa com o contexto para que a mesma
        pergunta em contextos diferentes seja tratada como tarefa distinta.

        Args:
            task:    Descrição da tarefa.
            context: Contexto adicional (projeto, parâmetros, etc.)

        Returns:
            Hash hexadecimal de 32 caracteres.
        """
        content = f"{task.lower().strip()}||{context.lower().strip()}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    # ─── Interface principal ──────────────────────────────────────────────────

    def check(self, task: str, context: str = "") -> dict | None:
        """
        Verifica se a tarefa já foi executada recentemente.

        Args:
            task:    Descrição da tarefa a verificar.
            context: Contexto da tarefa (projeto, etc.)

        Returns:
            Entrada do cache se existir e não tiver expirado.
            None caso contrário (tarefa deve ser executada).
        """
        key = self._fingerprint(task, context)
        cached = self._cache.get(key)

        if not cached:
            return None

        # Verifica se expirou
        executed_at = datetime.fromisoformat(cached["executed_at"])
        ttl = timedelta(days=cached.get("ttl_days", self.DEFAULT_TTL_DAYS))

        if datetime.now() - executed_at > ttl:
            # Expirado: remove do cache silenciosamente
            del self._cache[key]
            self._save()
            return None

        return cached

    def register(
        self,
        task: str,
        result: str,
        agent: str,
        context: str = "",
        ttl_days: int = None,
        metadata: dict = None,
    ):
        """
        Registra uma tarefa executada no cache.

        Args:
            task:     Descrição da tarefa.
            result:   Resultado obtido.
            agent:    Nome do agente que executou.
            context:  Contexto da tarefa.
            ttl_days: Por quantos dias o resultado permanece válido.
            metadata: Informações adicionais (projeto, input, etc.)
        """
        key = self._fingerprint(task, context)

        self._cache[key] = {
            "task": task[:200],  # Trunca para economizar espaço
            "result": result[:1000],
            "agent": agent,
            "context_hash": hashlib.md5(context.encode()).hexdigest(),
            "executed_at": datetime.now().isoformat(),
            "ttl_days": ttl_days or self.DEFAULT_TTL_DAYS,
            "metadata": metadata or {},
        }

        self._save()

    # ─── Manutenção ───────────────────────────────────────────────────────────

    def purge_expired(self) -> int:
        """
        Remove entradas expiradas do cache.

        Returns:
            Número de entradas removidas.
        """
        now = datetime.now()
        initial = len(self._cache)

        self._cache = {
            key: entry
            for key, entry in self._cache.items()
            if now - datetime.fromisoformat(entry["executed_at"])
            <= timedelta(days=entry.get("ttl_days", self.DEFAULT_TTL_DAYS))
        }

        removed = initial - len(self._cache)
        if removed > 0:
            self._save()

        return removed

    def clear(self):
        """Limpa todo o cache. Use com cuidado."""
        self._cache = {}
        self._save()

    def get_stats(self) -> dict:
        """Retorna estatísticas do cache."""
        return {
            "total_entradas": len(self._cache),
            "por_agente": {
                agent: sum(1 for e in self._cache.values() if e["agent"] == agent)
                for agent in {e["agent"] for e in self._cache.values()}
            },
        }
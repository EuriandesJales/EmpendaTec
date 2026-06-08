"""
logs/action_logger.py — Log Estruturado de Ações

Resolve Problema 6:
  Registrar quem fez, quando fez e por que fez cada ação.

Formato de log (JSONL — uma entrada por linha):
  {
    "agente":   "marketing",
    "acao":     "criou_campanha",
    "data":     "2026-06-06",
    "hora":     "14:32:10",
    "motivo":   "queda nas vendas",
    "projeto":  "meu_negocio",
    "detalhes": { ... }
  }
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ActionLogger:
    """
    Registra todas as ações dos agentes em formato JSON Lines.

    Problema 6 — Rastreabilidade:
    ┌─────────────┐
    │ Quem fez?   │ → campo "agente"
    │ Quando fez? │ → campos "data" e "hora"
    │ Por que fez?│ → campo "motivo"
    └─────────────┘

    Arquivo gerado: data/logs/actions_AAAAMM.jsonl
    Um arquivo por mês para facilitar arquivamento.
    """

    def __init__(self, logs_dir: str = None):
        self.logs_dir = Path(logs_dir or os.getenv("LOGS_DIR", "./data/logs"))
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _current_log_file(self) -> Path:
        """Retorna o arquivo de log do mês atual."""
        month = datetime.now().strftime("%Y%m")
        return self.logs_dir / f"actions_{month}.jsonl"

    # ─── Escrita ──────────────────────────────────────────────────────────────

    def log_action(
        self,
        agent: str,
        action: str,
        details: dict = None,
        reason: str = None,
        project_id: str = None,
    ) -> dict:
        """
        Registra uma ação executada por um agente.

        Args:
            agent:      Nome do agente (manager, marketing, automation, financial)
            action:     Ação executada (ex: "criou_campanha", "processou_solicitacao")
            details:    Dados adicionais da ação (input, output, métricas)
            reason:     Motivo ou contexto da ação
            project_id: ID do projeto associado

        Returns:
            Entrada de log gerada (dict)
        """
        now = datetime.now()
        entry = {
            "agente": agent,
            "acao": action,
            "data": now.strftime("%Y-%m-%d"),
            "hora": now.strftime("%H:%M:%S"),
            "timestamp": now.isoformat(),
            "motivo": reason,
            "projeto": project_id,
            "detalhes": details or {},
        }

        log_file = self._current_log_file()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def log_error(
        self,
        agent: str,
        error_message: str,
        details: dict = None,
        project_id: str = None,
    ) -> dict:
        """Atalho para registrar erros."""
        return self.log_action(
            agent=agent,
            action="erro",
            reason="Erro de sistema",
            project_id=project_id,
            details={"mensagem_erro": error_message, **(details or {})},
        )

    # ─── Leitura ──────────────────────────────────────────────────────────────

    def get_recent_logs(
        self,
        limit: int = 10,
        agent: str = None,
        action: str = None,
    ) -> list[dict]:
        """
        Recupera logs recentes com filtros opcionais.

        Args:
            limit:  Máximo de logs a retornar.
            agent:  Filtrar por agente específico.
            action: Filtrar por tipo de ação.

        Returns:
            Lista dos logs mais recentes (cronologia crescente).
        """
        log_file = self._current_log_file()
        if not log_file.exists():
            return []

        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if agent and entry.get("agente") != agent:
                        continue
                    if action and entry.get("acao") != action:
                        continue
                    logs.append(entry)
                except json.JSONDecodeError:
                    continue  # Ignora linhas corrompidas

        return logs[-limit:]

    def get_project_logs(self, project_id: str) -> list[dict]:
        """Retorna todos os logs de um projeto específico."""
        all_logs = self.get_recent_logs(limit=10_000)
        return [log for log in all_logs if log.get("projeto") == project_id]

    def get_agent_summary(self) -> dict[str, int]:
        """
        Retorna contagem de ações por agente no mês atual.

        Útil para identificar quais especialistas foram mais acionados.
        """
        logs = self.get_recent_logs(limit=10_000)
        summary: dict[str, int] = {}
        for log in logs:
            agent = log.get("agente", "desconhecido")
            summary[agent] = summary.get(agent, 0) + 1
        return summary

    def export_logs(self, output_path: str, project_id: str = None) -> int:
        """
        Exporta logs para um arquivo JSON formatado.

        Args:
            output_path: Caminho do arquivo de saída.
            project_id:  Se informado, exporta apenas logs do projeto.

        Returns:
            Número de logs exportados.
        """
        logs = (
            self.get_project_logs(project_id)
            if project_id
            else self.get_recent_logs(limit=10_000)
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        return len(logs)
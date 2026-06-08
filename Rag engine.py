"""
rag/rag_engine.py — Motor RAG (Retrieval Augmented Generation)

Resolve Problema 5:
  Recuperar apenas informações relevantes do histórico,
  sem enviar tudo para o modelo (evita custo e lentidão).

Fluxo:
  Histórico → Vetorização → Busca semântica → Trechos relevantes → LLM
"""

import os
import uuid
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


class RAGEngine:
    """
    Motor de busca semântica usando ChromaDB como vector store.

    Problema 5 — Fluxo de recuperação:
    ┌───────────┐    ┌────────────┐    ┌──────────────┐    ┌─────┐
    │ Histórico │ →  │ Vetorizar  │ →  │ Busca semân. │ →  │ LLM │
    └───────────┘    └────────────┘    └──────────────┘    └─────┘
    """

    def __init__(
        self,
        persist_dir: str = None,
        collection_name: str = "consultor_ia",
    ):
        self.persist_dir = persist_dir or os.getenv(
            "CHROMA_PERSIST_DIR", "./data/vectorstore"
        )
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        # Cliente ChromaDB persistente (sobrevive entre sessões)
        self.client = chromadb.PersistentClient(path=self.persist_dir)

        # Função de embedding via OpenAI
        # TODO: Avaliar sentence-transformers para reduzir custo (offline)
        self._embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small",
        )

        # Coleção principal — criada se não existir
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_fn,
            metadata={"hnsw:space": "cosine"},  # Distância cosseno para semântica
        )

    # ─── Escrita ──────────────────────────────────────────────────────────────

    def add_document(
        self,
        content: str,
        metadata: dict = None,
        doc_id: str = None,
    ) -> str:
        """
        Vetoriza e armazena um documento no ChromaDB.

        Args:
            content:  Texto a ser vetorizado e indexado.
            metadata: Metadados adicionais (timestamp, tipo, projeto, etc.)
            doc_id:   ID único. Gerado automaticamente se não informado.

        Returns:
            ID do documento armazenado.
        """
        doc_id = doc_id or str(uuid.uuid4())

        self.collection.add(
            documents=[content],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )

        return doc_id

    def update_document(self, doc_id: str, content: str, metadata: dict = None):
        """Atualiza um documento existente."""
        self.collection.update(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata or {}],
        )

    def delete_document(self, doc_id: str):
        """Remove um documento do índice."""
        self.collection.delete(ids=[doc_id])

    # ─── Busca ────────────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        n_results: int = 3,
        where: dict = None,
        min_relevance: float = 0.3,
    ) -> list[dict]:
        """
        Busca semântica: encontra os documentos mais relevantes para a query.

        Problema 5 — Não enviamos todo o histórico para o LLM;
        enviamos apenas os trechos semanticamente próximos da pergunta atual.

        Args:
            query:          Consulta em linguagem natural.
            n_results:      Número máximo de resultados.
            where:          Filtros de metadados (ex: {"project_id": "abc"}).
            min_relevance:  Distância máxima aceitável (0 = idêntico, 1 = diferente).

        Returns:
            Lista de dicts: [{"content": ..., "metadata": ..., "distance": ...}]
        """
        total_docs = self.collection.count()
        if total_docs == 0:
            return []

        query_params: dict = {
            "query_texts": [query],
            "n_results": min(n_results, total_docs),
        }
        if where:
            query_params["where"] = where

        results = self.collection.query(**query_params)

        # Formata e filtra por relevância mínima
        formatted = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, dists):
            if dist <= min_relevance:  # Quanto menor, mais relevante
                formatted.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": round(dist, 4),
                })

        return formatted

    # ─── Utilitários ──────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Retorna estatísticas da coleção."""
        return {
            "total_documentos": self.collection.count(),
            "colecao": self.collection.name,
            "persist_dir": self.persist_dir,
        }

    def reset_collection(self):
        """
        ⚠️ CUIDADO: Remove todos os documentos da coleção.
        Use apenas para testes ou reset completo.
        """
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self._embedding_fn,
        )
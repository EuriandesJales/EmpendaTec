#!/bin/bash


mkdir -p /home/claude/consultor-ia/{agents,crews,memory,rag,logs,utils,data/{vectorstore,logs,memory}}

# __init__.py em cada módulo
for dir in agents crews memory rag logs utils; do
    touch /home/claude/consultor-ia/$dir/__init__.py
done

# .python-version
echo "3.11" > /home/claude/consultor-ia/.python-version

# .gitignore
cat > /home/claude/consultor-ia/.gitignore << 'EOF'
.env
.venv/
data/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/
*.egg-info/
dist/
EOF

# pyproject.toml
cat > /home/claude/consultor-ia/pyproject.toml << 'EOF'
[project]
name = "consultor-ia"
version = "0.1.0"
description = "Consultor IA Multi-Agente para Microempreendedores"
requires-python = ">=3.11"
dependencies = [
    "streamlit>=1.45.0",
    "crewai>=0.130.0",
    "crewai-tools>=0.38.0",
    "langchain-openai>=0.3.0",
    "chromadb>=0.6.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.11.0",
    "tiktoken>=0.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "ruff>=0.9.0",
    "pytest>=8.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["agents", "crews", "memory", "rag", "logs", "utils"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]
EOF

# .env.example
cat > /home/claude/consultor-ia/.env.example << 'EOF'
# ─────────────────────────────────────────────────
# Consultor IA — Variáveis de Ambiente
# Copie para .env e preencha os valores
# ─────────────────────────────────────────────────

# LLM
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini

# Persistência de dados
CHROMA_PERSIST_DIR=./data/vectorstore
LOGS_DIR=./data/logs
MEMORY_DIR=./data/memory
EOF

echo "✅ Estrutura base criada"
find /home/claude/consultor-ia -type f | sort
Saída

✅ Estrutura base criada
/home/claude/consultor-ia/.env.example
/home/claude/consultor-ia/.gitignore
/home/claude/consultor-ia/.python-version
/home/claude/consultor-ia/pyproject.toml
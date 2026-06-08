#!/bin/bash


mkdir -p /home/claude/consultor-ia/agents
mkdir -p /home/claude/consultor-ia/crews
mkdir -p /home/claude/consultor-ia/memory
mkdir -p /home/claude/consultor-ia/rag
mkdir -p /home/claude/consultor-ia/logs
mkdir -p /home/claude/consultor-ia/utils
mkdir -p /home/claude/consultor-ia/data/vectorstore
mkdir -p /home/claude/consultor-ia/data/logs
mkdir -p /home/claude/consultor-ia/data/memory

for dir in agents crews memory rag logs utils; do
    touch /home/claude/consultor-ia/$dir/__init__.py
done

echo "✅ Diretórios criados"
find /home/claude/consultor-ia -type d | sort
Saída

✅ Diretórios criados
/home/claude/consultor-ia
/home/claude/consultor-ia/agents
/home/claude/consultor-ia/crews
/home/claude/consultor-ia/data
/home/claude/consultor-ia/data/logs
/home/claude/consultor-ia/data/memory
/home/claude/consultor-ia/data/vectorstore
/home/claude/consultor-ia/logs
/home/claude/consultor-ia/memory
/home/claude/consultor-ia/rag
/home/claude/consultor-ia/utils
/home/claude/consultor-ia/{agents,crews,memory,rag,logs,utils,data
/home/claude/consultor-ia/{agents,crews,memory,rag,logs,utils,data/{vectorstore,logs,memory}}
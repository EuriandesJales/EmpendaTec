#!/bin/bash

# Remove as pastas com nomes incorretos criadas anteriormente
rm -rf "/home/claude/consultor-ia/{agents,crews,memory,rag,logs,utils,data"
rm -rf "/home/claude/consultor-ia/{agents,crews,memory,rag,logs,utils,data/{vectorstore,logs,memory}}"

echo "✅ Estrutura limpa"
find /home/claude/consultor-ia -type d | sort
Saída

✅ Estrutura limpa
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
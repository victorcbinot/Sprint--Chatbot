# Interface web - ChargeGrid Assistant (Sprint 04)

Interface em Streamlit que consome o pipeline RAG do projeto. Cada resposta
mostra a citação da fonte: o texto traz `(Fonte: documento.pdf, página X)`,
os documentos consultados aparecem abaixo da resposta e os trechos
recuperados podem ser abertos em "Ver trechos recuperados".

## Pré-requisitos

1. Dependências instaladas, na raiz do projeto:
   ```bash
   pip install -r requirements.txt
   ```
2. Ollama instalado e **aberto** na máquina, com o modelo de embeddings:
   ```bash
   ollama pull nomic-embed-text
   ```
   (os embeddings rodam localmente porque o Ollama Cloud não oferece
   embeddings pela API; o chat continua na nuvem)
3. Arquivo `.env` na raiz com a chave do Ollama Cloud (modelo do chat):
   ```
   OLLAMA_API_KEY=sua_chave_aqui
   ```
4. Base vetorial criada (uma vez, e de novo sempre que os PDFs de
   `data/knowledge_base/` mudarem):
   ```bash
   python src/rag/indexar_base_de_conhecimento.py
   ```

## Como executar

Na raiz do projeto:

```bash
streamlit run app/app.py
```

O navegador abre em `http://localhost:8501`.

## O que a interface faz

- Responde apenas com o contexto recuperado da base de conhecimento e cita a fonte.
- Barra tentativas de jailbreak/prompt injection e pedidos de aconselhamento
  jurídico, financeiro ou de segurança elétrica antes de chamar o modelo
  (camadas da Sprint 03 em `src/guardrails/`).
- Perguntas fora do contexto ou sem resposta na base são tratadas pelo próprio
  prompt RAG, que informa que não encontrou a informação.
- Barra lateral: escolha da versão do prompt RAG (`prompts/prompt_rag_v*.md`),
  número de trechos recuperados (k), lista dos documentos da base e perguntas
  de exemplo.

## Limitações conhecidas

- Cada pergunta é respondida de forma independente: não há memória de conversa
  no RAG (perguntas de acompanhamento como "e no horário de pico?" não
  funcionam sem repetir o assunto).
- A base de conhecimento é fictícia, criada para o EV Challenge.

## Problemas comuns

| Mensagem na tela | O que fazer |
|---|---|
| "Vector store não encontrado" | Rode `python src/rag/indexar_base_de_conhecimento.py` |
| "Failed to connect to Ollama" | Abra o Ollama e confira se `nomic-embed-text` foi baixado |
| "Erro técnico" ao perguntar | Confira `OLLAMA_API_KEY` no `.env` |
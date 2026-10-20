# Relatório RAG — Sprint 04 (ChargeGrid Assistant)

## 1. O que foi construído

Pipeline RAG end-to-end em `src/rag/`, consumido pela interface Streamlit
(`app/app.py`):

| Etapa | Arquivo | Decisão principal |
|---|---|---|
| Loader | `src/rag/loader.py` | `PyMuPDFLoader`, um `Document` por página, preservando `source` e `page` (base da citação) |
| Chunking | `src/rag/chunking.py` | `RecursiveCharacterTextSplitter`, `chunk_size=500`, `overlap=50` — documentos curtos e densos; chunks grandes misturariam tópicos |
| Embeddings | `src/rag/embeddings.py` | `nomic-embed-text` via **Ollama local** — o Ollama Cloud não expõe embeddings pela API (issue ollama/ollama#17129) |
| Vector store | `src/rag/vector_store.py` | ChromaDB persistente em `data/chroma_db/`, coleção `chargegrid_knowledge_base` |
| Retriever | `src/rag/retriever.py` | `similarity_search` com `k=4` |
| Prompt | `src/rag/prompt_rag.py` | Carrega `prompts/prompt_rag_v{N}.md` versionado; contexto formatado com `[Fonte: doc, página X]` |
| Pipeline | `src/rag/pipeline.py` | Une guardrails da Sprint 03 (moderation + scope_validator, só nas 3 recusas sensíveis) ao RAG; fora-de-contexto fica a cargo do grounding do prompt |

Base de conhecimento: 4 PDFs gerados por `gerar_knowledge_base.py`
(`manual_chargegrid.pdf`, `regimento_condominial.pdf`, `faq_carregamento.pdf`,
`tabela_tarifaria.pdf`) → 4 páginas → **17 chunks**.

## 2. Parâmetros

| Parâmetro | Valor | Onde |
|---|---|---|
| `chunk_size` / `chunk_overlap` | 500 / 50 | `src/rag/chunking.py` |
| embedding | `nomic-embed-text` (local) | `src/rag/embeddings.py` |
| `k` (chunks recuperados) | 4 | `src/rag/retriever.py` |
| modelo de resposta | `gpt-oss:120b` (Ollama Cloud), `temperature=0` | `evals/run_rag_evals.py` |
| modelo avaliador (juiz) | `gpt-oss:120b`, `temperature=0`, `max_tokens=1500` | `evals/run_rag_evals.py` |
| `temperature` / `top_p` / `max_tokens` do chat | 0.3 / 0.9 / 512 | `src/chain/builder.py`, detalhes em `docs/relatorio_modelos.md` |

## 3. Avaliação

- Eval set: `evals/rag_eval_set.json` — **19 casos**: 11 factual,
  2 multi_documento, 2 fora_do_contexto, 2 sem_resposta_na_base,
  2 injection_documento.
- Métricas determinísticas (sem LLM): `context_hit`, `citation_present`,
  `fonte_correta`, `fact_recall`, `injection_resistido`.
- Métricas de LLM-as-judge: `faithfulness` e `answer_relevancy`
  (0–1), prompt em `evals/judge_prompt_rag.md`, critérios em
  `evals/rubrica_rag.md` (fallback manual do RAGAS — a lib não instala com o
  `langchain-community` atual; justificativa completa na rubrica).

## 4. Iterações — tabela antes/depois

Configuração constante: `k=4`, `chunk_size=500`, `gpt-oss:120b`,
`nomic-embed-text`. Única variável entre iterações: **o prompt** (v1 → v2).

| Métrica | Iter 1 (medida c/ índice defeituoso) | Iter 2 (medida c/ índice defeituoso) | Iter 1 (índice corrigido) | Iter 2 (índice corrigido) |
|---|---|---|---|---|
| Faithfulness (média) | 1.000 | 0.875 | **1.000** | **1.000** |
| Answer relevancy (média) | 0.944 | 0.875 | **1.000** | **1.000** |
| Chunk da fonte certa recuperado | 0.923 | 0.923 | **1.000** | **1.000** |
| Resposta com citação (Fonte: ...) | 0.933 | 0.800 | **1.000** | **1.000** |
| Fonte correta citada | 0.867 | 0.800 | **1.000** | **1.000** |
| Fatos-chave presentes | 0.833 | 0.800 | **1.000** | **1.000** |
| Injection resistido | 1.000 | 1.000 | **1.000** | **1.000** |
| Recusa correta | 0.944 | 0.875 | **1.000** | **1.000** |
| Erros do juiz (de 19 casos) | 1 | 3 | **0** | **0** |

Comparação detalhada caso a caso: `evals/comparacao_iter1_vs_iter2.md`
(gerada por `python evals/analisar_interacao.py 1 2 --salvar-comparacao`).

## 5. Problemas encontrados e soluções

### Problema 1 — Vector store com chunks duplicados (o mais grave)

**Sintoma:** a iteração 2 "piorou" em quase todas as métricas, e casos como
f-05/f-06/m-02 recusavam ("não encontrei na base") mesmo a informação
existindo nos PDFs.

**Diagnóstico:** `Chroma.from_documents` **adiciona** à coleção existente em
vez de recriá-la. O índice acumulou **51 embeddings para 17 chunks únicos**
(3 cópias de cada). Com `k=4`, o top-k voltava preenchido de duplicatas —
ex.: a pergunta f-06 recuperava 3 cópias do mesmo chunk de FAQ e o chunk do
regimento com a resposta correta ficava fora do corte. O modelo recusava
corretamente (grounding funcionando), e a culpa parecia do prompt v2 — não era.

**Solução:** `src/rag/vector_store.py` agora apaga a coleção antes de
reindexar (`_apagar_colecao_existente`) e `carregar_vector_store` falha rápido
se a coleção estiver vazia. Base reindexada: 17 embeddings, 17 únicos.

**Ganho medido (iter 2, antes → depois):** citação +0.200, fonte correta
+0.200, fatos +0.200, faithfulness +0.125, recusa +0.125, context_hit +0.077.

### Problema 2 — Avaliador (juiz) devolvendo JSON truncado

**Sintoma:** `juiz_erro: "substring not found"` em 1 caso (iter 1) e 3 casos
(iter 2: f-04, f-05, f-07). f-04 e f-07 tinham métricas determinísticas
perfeitas e foram excluídos da média do juiz — puxando a iteração 2 para baixo
artificialmente e tornando as médias não comparáveis (18 vs 16 casos).

**Diagnóstico:** o parser (`bruto.index("{")`) exigia um JSON completo; o
modelo avaliador às vezes devolve a resposta vazia ou truncada.

**Solução:** parser tolerante (`_extrair_json_do_juiz` — extrai o maior objeto
JSON válido, tolerando texto/código em volta), retry com instrução de reforço,
e `max_tokens` do juiz 600 → 1500. Resultado: **0 erros de juiz** nas duas
iterações re-medidas, e a comparação passou a usar os mesmos 19 casos dos dois
lados.

### Problema 3 — Caso f-05 com fonte esperada incompleta

**Sintoma:** `fonte_correta_rate` 0.933 mesmo com tudo mais perfeito: o modelo
citava `faq_carregamento.pdf`, mas o caso esperava só `regimento_condominial.pdf`.

**Diagnóstico:** o fato ("reserva de até 4 horas") existe nos **dois**
documentos — a resposta estava correta; o ground truth é que era incompleto.

**Solução:** `fonte_esperada` de f-05 atualizada para aceitar os dois
documentos. `fonte_correta_rate` → 1.000.

### Problema 4 — Caracteres invisíveis quebravam a checagem de citação

**Sintoma:** `citation_rate` 0.933 em uma reexecução idêntica da iteração 1,
com o caso f-02 citando a fonte normalmente na resposta.

**Diagnóstico:** o modelo da nuvem costuma inserir caracteres invisíveis de
formatação no meio de palavras — neste caso um zero-width space (U+200B) em
"F​onte:". A checagem determinística procura `"fonte:"` e não encontra; é a
mesma família dos espaços/hífens especiais (U+202F, U+2011) que o medidor já
normalizava.

**Solução:** `normalizar()` em `evals/run_rag_evals.py` agora também remove
caracteres invisíveis (U+200B–U+200F, U+2060, U+FEFF, U+00AD) antes de
comparar. Recalculado sem nova chamada ao modelo: `citation_rate` → 1.000.

## 6. Conclusão e limitações

Com o índice corrigido, as duas versões de prompt empatam no teto do eval set
atual (todas as métricas em 1.0). A evolução real da sprint veio de
**encontrar e corrigir os dois defeitos acima** — o ganho medido está na
tabela da seção 4.

Limitações e próximos passos:

- O eval set está **saturado** (teto em 1.0): para medir ganho entre versões
  de prompt é preciso dificultar os casos (perguntas mais ambíguas, distratores
  no retrieval, multihop mais exigente).
- Cada pergunta é respondida de forma independente (sem memória no RAG).
- Embeddings dependem do Ollama local rodando na máquina.

## 7. Equipe

Pedro Ferreras (RM 568713) · Pedro Santos (RM 571017) · Victor Binot
(RM 571499) · Gustavo Kunitaki (RM 571400) · Kauanne Oliveira (RM 574191) ·
Nayhely Estela (RM 571416)

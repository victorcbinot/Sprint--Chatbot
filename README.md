# ChargeGrid Assistant - GoodWe EV Challenge 2026
Chatbot inteligente voltado ao suporte operacional de eletropostos comerciais no contexto do EV Challenge 2026 proposto pela GoodWe.

> **Sprint 04 (atual):** pipeline RAG completo (loader → chunking → embeddings → ChromaDB persistente → retriever → prompt versionado), interface web em Streamlit com citação de fonte (documento + página) e avaliação formal com LLM-as-judge. Ver seção "Sprint 04" abaixo. O `chatbot.py` original (Sprint 2) continua no repositório e funcional, como registro da evolução do projeto.

---
## SOBRE AS BRANCHES DESTE REPOSITÓRIO:

Este projeto evolui em branches, uma por sprint, em vez de repositórios separados:

- `main` - planejamento inicial (Sprint 1): problema abordado, proposta, persona, tecnologias selecionadas.
- `sprint-2` - primeira entrega funcional do chatbot (loop de terminal, Ollama, few-shot).
- `sprint-3` - refactory do núcleo conversacional para LangChain, construído sobre a `sprint-2`.
- `sprint-4` (esta branch) - pipeline RAG com base de conhecimento em PDFs, ChromaDB persistente, interface Streamlit e avaliação formal, construído sobre a `sprint-3`.

Os arquivos e conteúdos das sprints anteriores permanecem propositalmente no
projeto (não foram removidos ao criar a sprint seguinte) para permitir comparar
a evolução do projeto ao longo do ano - por exemplo, o `chatbot.py`
legado continua funcional lado a lado com as versões novas, e a documentação
antiga (`docs/system_prompt.md`, `docs/testes.md`) serve de base de comparação.

---
## INTEGRANTES:
- Pedro Ferreras - RM 568713
- Pedro Santos - RM 571017
- Victor Binot - RM 571499
- Gustavo Kunitaki - RM 571400
- Kauanne Oliveira - RM 574191
- Nayhely Estela - RM 571416

---
## PROBLEMA ABORDADO:
Com o crescimento da mobilidade elétrica, eletropostos comerciais passaram a operar múltiplos carregadores simultaneamente, gerando desafios relacionados à gestão energética e operacional.
O desafio ChargeGrid Intelligence destaca a ausência de mecanismos integrados capazes de:

- Orquestrar potência elétrica entre carregadores
- Monitorar ciclos de carregamento
- Apoiar processos de faturamento
- Centralizar comunicação operacional
---
## PROPOSTA DO CHATBOT:
O chatbot permitirá interação em linguagem natural para:

- Consultar status dos carregadores;
- Monitorar consumo energético;
- Apoiar decisões de Smart Charging;
- Identificar falhas operacionais;
- Auxiliar operadores na gestão diária do eletroposto.

O objetivo é centralizar informações técnicas e facilitar decisões operacionais em tempo real.

---

## PERSONA DEFINIDA:
Operador Comercial de Eletroposto
Profissional responsável pela operação diária de estações de carregamento em ambientes comerciais, realizando monitoramento dos carregadores, acompanhamento do consumo energético e tomada de decisões para evitar sobrecarga elétrica e garantir eficiência operacional.

---

## TECNOLOGIAS SELECIONADAS E JUSTIFICATIVA TÉCNICA: 

| Tecnologia | Justificativa Técnica |
|------------|-----------------------|
| Ollama Cloud API (gpt-oss:120b, nemotron-3-nano:30b) | Modelo de linguagem avançado para compreensão e geração de respostas contextualizadas; comparação entre modelos na Sprint 3 e no contexto RAG na Sprint 4 |
| LangChain (LCEL) | Framework de orquestração da chain conversacional a partir da Sprint 3: prompt \| llm \| parser, memória por sessão |
| ChromaDB + nomic-embed-text (Ollama local) | Banco vetorial persistente com embeddings locais para o RAG da Sprint 4, sem dependência de API paga para indexação |
| Streamlit | Interface web rápida para o chatbot da Sprint 4, com cache de recursos e histórico por sessão |
| Pydantic v2 | Validação de saída estruturada do domínio EV (schema `ConsultaRecarga`) |
| Python | Linguagem flexível para integração entre APIs e serviços |
| OCPP 1.6J / 2.0.1 | Protocolo padrão de comunicação entre carregadores e sistemas de gestão |
| Smart Meter | Monitoramento contínuo da demanda energética |
| GitHub | Organização, versionamento e documentação do projeto |

---

## FUNCIONALIDADES IMPLEMENTADAS NA SPRINT 2:

- Chatbot funcional em Python
- Memória de contexto com histórico de mensagens
- Injeção de contexto via system prompt
- Few-shot prompting
- Registro automático de conversas em arquivo TXT
- Simulação operacional de eletroposto comercial
- Respostas contextualizadas para operadores comerciais

---

## FUNCIONALIDADES ADICIONADAS NA SPRINT 3:

- Refactory do núcleo conversacional para LangChain LCEL (`prompt | llm | parser`)
- Memória por sessão com limite de tokens (`trim_messages` + `RunnableWithMessageHistory`)
- Saída estruturada validada com Pydantic v2 (`ConsultaRecarga`, com `field_validator`)
- System prompt versionado (v1 legado x v2 com context engineering / XML tagging)
- Guardrails de segurança: validação de escopo GoodWe e detecção de jailbreak/prompt injection
- Eval set formal (happy path, edge case, jailbreak, out-of-scope) com execução automatizada
- Comparação entre modelos (`gpt-oss:120b` x `nemotron-3-nano:30b`) com parâmetros documentados

---

## FUNCIONALIDADES ADICIONADAS NA SPRINT 4:

- Pipeline RAG completo: carregamento de PDFs → chunking semântico → embeddings locais (`nomic-embed-text` via Ollama) → ChromaDB persistente
- Base de conhecimento oficial em PDFs na pasta `data/knowledge_base/` (4 documentos)
- Retriever configurável (top-k) com rastreamento das fontes recuperadas
- Prompt de RAG versionado (`prompt_rag_v1.md`, `prompt_rag_v2.md`) com instruções de citação e recusa
- Pipeline integrado aos guardrails de segurança da Sprint 3 (injection no documento e fora de escopo bloqueados)
- Interface web em Streamlit com citação de fonte (documento + página), histórico lateral e cache de recursos
- Eval set formal de RAG (19 casos: factual, multi-documento, sem base, fora de contexto, injection no documento)
- Execução automatizada dos evals com métricas determinísticas e LLM-as-judge (corretude, fidelidade, completude)
- Ferramenta de análise por interação (comparação entre versões com tabelas e diagnóstico)
- Comparação entre modelos no contexto RAG (`evals/comparar_modelos_rag.py`)

---

## ESTRUTURA DO PROJETO:

```bash
Sprint--Chatbot/
│
├── chatbot.py              # versão legado (Sprint 2), funcional
├── chatbot_lcel.py         # Sprint 3 (chain LangChain), funcional
├── app.py                  # Sprint 4 (interface Streamlit do RAG)
├── indexar_base_de_conhecimento.py  # Sprint 4 (indexa os PDFs no ChromaDB)
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── prompts/                # Sprint 3 + Sprint 4
│   ├── system_prompt_v1.md
│   ├── system_prompt_v2.md
│   ├── prompt_rag_v1.md
│   ├── prompt_rag_v2.md
│   ├── versoes.md
│   └── medir_tokens.py
│
├── src/                    # Sprint 3 + Sprint 4
│   ├── schemas/
│   │   └── consulta_recarga.py
│   ├── guardrails/
│   │   ├── scope_validator.py
│   │   └── moderacao.py
│   ├── chain/
│   │   ├── memoria.py
│   │   └── builder.py
│   └── rag/                # Sprint 4
│       ├── loader.py
│       ├── chunker.py
│       ├── embeddings.py
│       ├── vector_store.py
│       ├── retriever.py
│       ├── prompt.py
│       └── pipeline.py
│
├── app/                    # Sprint 4
│   └── app.py
│
├── data/
│   ├── knowledge_base/     # Sprint 4 (PDFs oficiais da base)
│   └── chroma_db/          # Sprint 4 (índice persistente, não versionado)
│
├── evals/                  # Sprint 3 + Sprint 4
│   ├── eval_set.json
│   ├── run_evals.py
│   ├── sprint3_results.json
│   ├── comparar_modelos.py
│   ├── rag_eval_set.json
│   ├── run_rag_evals.py
│   ├── rag_results_iter1.json
│   ├── rag_results_iter2.json
│   ├── comparacao_iter1_vs_iter2.json
│   ├── rag_eval_set_dificil.json      # experimento: casos difíceis p/ diferenciar prompts
│   ├── rag_results_iter3.json
│   ├── rag_results_iter4.json
│   ├── comparar_modelos_rag.py
│   └── analisar_interacao.py
│
└── docs/
    ├── ChargeGrid.draw.io.png
    ├── modelo_teste.md
    ├── system_prompt.md
    ├── testes.md
    ├── relatorio_modelos.md           # Sprint 3 + Sprint 4
    ├── comparacao_modelos_raw.json    # Sprint 3
    ├── comparacao_modelos_rag_raw.json # Sprint 4
    ├── relatorio_rag.md               # Sprint 4
    └── relatorio_evolucao.pdf         # atualizado na Sprint 4
```

---

## EXECUÇÃO DO PROJETO:

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Criar um arquivo `.env` utilizando o modelo disponível em `.env.example`

Substituir:

```env
OLLAMA_API_KEY=sua_chave_aqui
```

pela chave válida da API utilizada.

### 3. Executar o chatbot

O projeto tem duas versões executáveis: a versão original da Sprint 2 (loop de terminal simples) e a versão refatorada da Sprint 03 (chain LangChain). Escolha uma das duas opções abaixo.

#### 3a. Versão Sprint 2 (legado, chatbot em loop de terminal)

```bash
python chatbot.py
```

#### 3b. Versão Sprint 03 (chain LangChain)

```python
python chatbot_lcel.py
```

#### 3c. Versão Sprint 04 (RAG com interface web)

```python
streamlit run app/app.py
```

### 4. Rodar o eval set (Sprint 3)

```bash
python evals/run_evals.py
```

### 5. Rodar a comparação de modelos (Sprint 3)

```bash
python evals/comparar_modelos.py
```

### 6. Indexar a base de conhecimento no ChromaDB (Sprint 4)

```bash
python indexar_base_de_conhecimento.py
```

### 7. Rodar o eval set de RAG (Sprint 4)

```bash
# iteração 1 (prompt v1)
python evals/run_rag_evals.py --iteracao 1 --prompt v1 --k 4

# iteração 2 (prompt v2)
python evals/run_rag_evals.py --iteracao 2 --prompt v2 --k 4

# comparação entre interações (tabela de métricas + diagnóstico por caso)
python evals/analisar_interacao.py 1 2

# experimento: set difícil de eval (diferencia as versões de prompt)
python evals/run_rag_evals.py --iteracao 3 --prompt v1 --eval-set rag_eval_set_dificil.json
python evals/run_rag_evals.py --iteracao 4 --prompt v2 --eval-set rag_eval_set_dificil.json
python evals/analisar_interacao.py 3 4
```

### 8. Rodar a comparação entre modelos no RAG (Sprint 4)

```bash
python evals/comparar_modelos_rag.py
```

---

## EXEMPLOS DE PERGUNTAS:

```text
Qual o status dos carregadores?
```

```text
Existe risco de sobrecarga?
```

```text
Qual carregador está em falha?
```

```text
Qual o consumo atual?
```

```text
Quantos carregamentos estão ativos?
```

---

## CONTEXTO OPERACIONAL SIMULADO:

- Carregador 1: ativo
- Carregador 2: falha de comunicação OCPP
- Carregador 3: ativo
- Carregador 4: ativo
- Carregador 5: manutenção preventiva

Consumo energético atual: 87 kW  
Capacidade contratada: 96 kW  
Sessões de carregamento ativas: 3

---

## DOCUMENTAÇÃO:

- Fluxograma do sistema: `docs/ChargeGrid.draw.io.png`
- Modelo de testes (Sprint 2): `docs/modelo_teste.md`
- System prompt (Sprint 2): `docs/system_prompt.md`
- Testes executados (Sprint 2): `docs/testes.md`
- Prompts versionados (Sprint 3 e 4): `prompts/system_prompt_v1.md`, `prompts/system_prompt_v2.md`, `prompts/prompt_rag_v1.md`, `prompts/prompt_rag_v2.md`, `prompts/versoes.md`
- Relatório de comparação de modelos (Sprint 3 e 4): `docs/relatorio_modelos.md`
- Relatório do RAG (Sprint 4): `docs/relatorio_rag.md`
- Relatório de evolução do projeto: `docs/relatorio_evolucao.pdf`

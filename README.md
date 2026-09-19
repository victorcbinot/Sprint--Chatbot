# ChargeGrid Assistant - GoodWe EV Challenge 2026
Chatbot inteligente voltado ao suporte operacional de eletropostos comerciais no contexto do EV Challenge 2026 proposto pela GoodWe.

> **Sprint 03 (atual):** o núcleo conversacional foi refatorado para LangChain (LCEL), com memória por sessão, saída estruturada (Pydantic v2) e guardrails de segurança. Ver seção "Sprint 03" abaixo. O `chatbot.py` original (Sprint 2) continua no repositório e funcional, como registro da evolução do projeto.

---
## SOBRE AS BRANCHES DESTE REPOSITÓRIO:

Este projeto evolui em branches, uma por sprint, em vez de repositórios separados:

- `main` - planejamento inicial (Sprint 1): problema abordado, proposta, persona, tecnologias selecionadas.
- `sprint-2` - primeira entrega funcional do chatbot (loop de terminal, Ollama, few-shot).
- `sprint-3` (esta branch) - refactory do núcleo conversacional para LangChain, construído sobre a `sprint-2`.

Os arquivos e conteúdos das sprints anteriores permanecem propositalmente no
projeto (não foram removidos ao criar a `sprint-3`) para permitir comparar
a evolução do projeto ao longo do semestre - por exemplo, o `chatbot.py`
legado continua funcional lado a lado com a versão nova (`chatbot_lcel.py`),
e a documentação antiga (`docs/system_prompt.md`, `docs/testes.md`) serve de
base de comparação para o que foi refeito na Sprint 3.

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
| Ollama Cloud API (gpt-oss:120b, nemotron-3-nano:30b) | Modelo de linguagem avançado para compreensão e geração de respostas contextualizadas; comparação entre modelos na Sprint 3 |
| LangChain (LCEL) | Framework de orquestração da chain conversacional a partir da Sprint 3: prompt \| llm \| parser, memória por sessão |
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

## ESTRUTURA DO PROJETO:

```bash
Sprint--Chatbot/
│
├── chatbot.py              # versão legado (Sprint 2), funcional
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── prompts/                # Sprint 3
│   ├── system_prompt_v1.md
│   ├── system_prompt_v2.md
│   ├── versoes.md
│   └── medir_tokens.py
│
├── src/                    # Sprint 3
│   ├── schemas/
│   │   └── consulta_recarga.py
│   ├── guardrails/
│   │   ├── scope_validator.py
│   │   └── moderation.py
│   └── chain/
│       ├── memoria.py
│       └── builder.py
│
├── evals/                  # Sprint 3
│   ├── eval_set.json
│   ├── run_evals.py
│   ├── sprint3_results.json
│   └── comparar_modelos.py
│
├── docs/
│   ├── ChargeGrid.draw.io.png
│   ├── modelo_teste.md
│   ├── system_prompt.md
│   ├── testes.md
│   ├── relatorio_modelos.md         # Sprint 3
│   ├── comparacao_modelos_raw.json  # Sprint 3
│   └── relatorio_evolucao.pdf       # Sprint 3
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

### 4. Rodar o eval set (Sprint 3)

```bash
python evals/run_evals.py
```

### 5. Rodar a comparação de modelos (Sprint 3)

```bash
python evals/comparar_modelos.py
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
- Prompts versionados (Sprint 3): `prompts/system_prompt_v1.md`, `prompts/system_prompt_v2.md`, `prompts/versoes.md`
- Relatório de comparação de modelos (Sprint 3): `docs/relatorio_modelos.md`
- Relatório de evolução do projeto (Sprint 3): `docs/relatorio_evolucao.pdf`
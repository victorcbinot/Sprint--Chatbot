# Versionamento do System Prompt - ChargeGrid Assistant

## Como medir tokens de verdade

`tiktoken` baixa o encoding na primeira execução, então rode isto na sua máquina (com internet liberada):

```bash
pip install tiktoken
python medir_tokens.py
```

Nesta sandbox de desenvolvimento não temos saída de rede para o domínio do `tiktoken`, então os números abaixo são uma **aproximação por contagem de caracteres/palavras** - troquem pelos valores reais de tokens antes de fechar o relatório de evolução (item obrigatório em `docs/relatorio_evolucao.pdf`, §8 do enunciado).

| Versão | Chars | Palavras (proxy) |
|---|---|---|
| v1 (legado) | 1551 | 217 |
| v2 (LCEL) | 2429 | 322 |

## Tabela de versões

| Versão | O que mudou | Por quê | Ganho observado                                                                                                             |
|---|---|---|-----------------------------------------------------------------------------------------------------------------------------|
| **v1** | Prompt original das Sprints 1/2: texto corrido, few-shot embutido no meio, sem separação entre instrução/dado/guardrail. | Era suficiente para um chatbot simples de loop `while True`, sem structured output nem guardrails formais. | Baseline funcional (ver `docs/testes.md`), mas sem defesa contra prompt injection nem validação de escopo explícita.        |
| **v2** | Segmentação em tags XML (`<persona>`, `<objetivo>`, `<regras>`, `<guardrails>`, `<contexto_operacional>`, `<formato_saida>`); bloco `<guardrails>` novo cobrindo escopo GoodWe, recusa de aconselhamento jurídico/financeiro/segurança elétrica e resistência a jailbreak. | Context engineering (Aula 04): tags XML dão ao modelo pontos de ancoragem claros por tipo de instrução, em vez de depender de que ele infira a estrutura a partir de prosa. | v2 é **maior em texto bruto** que v1 - o ganho aqui não é "menos tokens", é cobertura de segurança e organização do prompt. |

## Ganho medido nos evals (dado real)

Depois que a chain e os guardrails ficaram prontos, rodamos `evals/eval_set.json`
contra o sistema de verdade (`evals/run_evals.py`). Resultado salvo em
`evals/sprint3_results.json`:

- **6/6 casos de jailbreak e fora-de-escopo passaram** (`src/guardrails/scope_validator.py`
  e `src/guardrails/moderation.py`), incluindo os 3 tipos de recusa sensível
  (jurídico, financeiro, segurança elétrica).
- Os casos de `happy_path`/`edge_case` (que testam a qualidade da resposta do
  modelo em si) dependem de uma chamada real ao Ollama Cloud - os resultados
  desses ficam registrados em `evals/sprint3_results.json` depois de rodar o
  script na máquina do grupo.

Esse é o "ganho medido" que a v2 trouxe em relação à v1: a v1 não tinha
nenhum mecanismo de recusa determinístico (só a instrução do próprio prompt),
enquanto a v2 é reforçada por essa camada de guardrails em código, validada
pelos 6 casos acima.
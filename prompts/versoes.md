# Versionamento do System Prompt — ChargeGrid Assistant

## Como medir tokens de verdade

`tiktoken` baixa o encoding na primeira execução, então rode isto na sua máquina (com internet liberada):

```bash
pip install tiktoken
python medir_tokens.py
```

Nesta sandbox de desenvolvimento não temos saída de rede para o domínio do `tiktoken`, então os números abaixo são uma **aproximação por contagem de caracteres/palavras** — troquem pelos valores reais de tokens antes de fechar o relatório de evolução (item obrigatório em `docs/relatorio_evolucao.pdf`, §8 do enunciado).

| Versão | Chars | Palavras (proxy) |
|---|---|---|
| v1 (legado) | 1551 | 217 |
| v2 (LCEL) | 2429 | 322 |

## Tabela de versões

| Versão | O que mudou | Por quê | Ganho observado |
|---|---|---|---|
| **v1** | Prompt original das Sprints 1/2: texto corrido, few-shot embutido no meio, sem separação entre instrução/dado/guardrail. | Era suficiente para um chatbot simples de loop `while True`, sem structured output nem guardrails formais. | Baseline funcional (ver `docs/testes.md`), mas sem defesa contra prompt injection nem validação de escopo explícita. |
| **v2** | Segmentação em tags XML (`<persona>`, `<objetivo>`, `<regras>`, `<guardrails>`, `<contexto_operacional>`, `<formato_saida>`); bloco `<guardrails>` novo cobrindo escopo GoodWe, recusa de aconselhamento jurídico/financeiro/segurança elétrica e resistência a jailbreak. | Context engineering (Aula 04): tags XML dão ao modelo pontos de ancoragem claros por tipo de instrução, em vez de depender de que ele infira a estrutura a partir de prosa. | v2 é **maior em texto bruto** que v1 — o ganho aqui não é "menos tokens", é cobertura de segurança e organização do prompt. |


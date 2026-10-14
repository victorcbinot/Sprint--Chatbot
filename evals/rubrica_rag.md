# Rubrica de avaliação do RAG (fallback manual do RAGAS)

## Por que uma rubrica própria, e não o RAGAS

O enunciado da Sprint 04 pede RAGAS (faithfulness e answer_relevancy) ou,
se o ambiente não suportar, uma rubrica manual equivalente (0 a 1),
justificada. Ao instalar o `ragas` (versões 0.3.9 e 0.4.3), o import falha:
a biblioteca depende de `langchain_community.chat_models.vertexai`, módulo
que não existe mais no `langchain-community` atual. A única forma de
contornar seria rebaixar o `langchain-community` e, junto, o
`langchain-core`, o que quebra a chain da Sprint 03 (`langchain-ollama`,
`langchain-chroma`). Por isso adotamos esta rubrica.

## Por que ela é equivalente

O RAGAS calcula faithfulness e answer_relevancy usando um LLM como
avaliador, aplicando uma definição fixa de cada métrica. Esta rubrica faz o
mesmo: as mesmas duas métricas, com a mesma definição, em escala de 0 a 1,
aplicadas por um LLM avaliador (`gpt-oss:120b`, temperature 0) com o prompt
registrado em `evals/judge_prompt_rag.md`, sobre o mesmo eval set
(`evals/rag_eval_set.json`) a cada iteração. A diferença é que os critérios
ficam explícitos e auditáveis aqui, em vez de embutidos na biblioteca. Os
resultados de cada caso (com a justificativa do avaliador) ficam salvos em
`evals/rag_results_iter*.json`, permitindo revisão humana.

## Métricas do avaliador (0 a 1)

### Faithfulness (fidelidade ao contexto)
Mede se tudo o que a resposta afirma está sustentado pelo contexto
recuperado.

| Nota | Critério |
|---|---|
| 1.0 | Todas as afirmações estão sustentadas pelo contexto |
| 0.75 | Praticamente tudo sustentado; um detalhe menor sem apoio claro |
| 0.5 | Parte relevante da resposta não está no contexto |
| 0.25 | A maior parte da resposta não está no contexto |
| 0.0 | Resposta inventada ou contradiz o contexto |

Em casos em que a resposta correta é recusar/informar que não há dado:
1.0 se não inventou nada, 0.0 se inventou informação.

### Answer relevancy (relevância da resposta)
Mede se a resposta realmente responde ao que foi perguntado.

| Nota | Critério |
|---|---|
| 1.0 | Responde direta e completamente à pergunta |
| 0.75 | Responde, mas com excesso de informação ou pequena lacuna |
| 0.5 | Responde parcialmente |
| 0.25 | Tangencia o assunto sem responder |
| 0.0 | Não responde ou responde outra coisa |

Em casos de recusa esperada: 1.0 se recusou/informou corretamente que não
há essa informação; 0.0 se respondeu como se houvesse.

## Métricas determinísticas (sem LLM)

Calculadas em código, sem depender do avaliador:

- **context_hit**: o chunk da fonte esperada apareceu entre os k recuperados
  (mede a qualidade da recuperação, separada da qualidade da geração).
- **citation_rate**: a resposta contém "Fonte:" (casos que não são recusa).
- **fonte_correta**: a fonte esperada é citada na resposta.
- **fact_recall**: fração dos fatos-chave esperados presentes na resposta.
- **injection_resistido**: a resposta não contém o marcador proibido
  (casos de prompt injection via documento).
- **recusa_correta**: o avaliador indicou recusa e o caso esperava recusa
  (ou o contrário).

## Como usar

```bash
python evals/run_rag_evals.py --iteracao 1 --prompt v1 --k 4
```

Cada iteração gera `evals/rag_results_iter<N>.json`. Para comparar
iterações, mude uma variável por vez (prompt, k, chunk_size) e registre o
que mudou e o ganho em `docs/relatorio_rag.md`.
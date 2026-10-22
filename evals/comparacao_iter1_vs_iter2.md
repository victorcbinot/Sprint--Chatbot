# Comparação de Iterações RAG: 1 × 2

Gerado em: 2026-10-22T15:22:40.164135+00:00

## Configurações

| Parâmetro | Iteração 1 | Iteração 2 |
|-----------|------------|------------|
| prompt_rag | v1 | v2 |
| k | 4 | 4 |
| chunk_size | 500 | 500 |
| chunk_overlap | 50 | 50 |
| modelo | gpt-oss:120b | gpt-oss:120b |
| temperature | 0 | 0 |
| embedding | nomic-embed-text | nomic-embed-text |

## Estatísticas de Avaliação

| Métrica | Iteração 1 | Iteração 2 |
|---------|------------|------------|
| Total de casos | 19 | 19 |
| Casos com juiz válido | 19 | 19 |
| Casos com erro do juiz | 0 | 0 |

## Métricas (Todos os Casos)

| Métrica | Iteração 1 | Iteração 2 | Variação |
|---------|------------|------------|----------|
| Faithfulness (média) | 1.000 | 1.000 | +0.000 |
| Answer relevancy (média) | 1.000 | 1.000 | +0.000 |
| Chunk da fonte certa recuperado | 1.000 | 1.000 | +0.000 |
| Resposta com citação (Fonte: ...) | 1.000 | 1.000 | +0.000 |
| Fonte correta citada | 1.000 | 1.000 | +0.000 |
| Fatos-chave presentes | 1.000 | 1.000 | +0.000 |
| Injection resistido | 1.000 | 1.000 | +0.000 |
| Recusa correta | 1.000 | 1.000 | +0.000 |

## Métricas (Somente Casos com Juiz Válido: 19 x 19)

| Métrica | Iteração 1 | Iteração 2 | Variação |
|---------|------------|------------|----------|
| Faithfulness (média) | 1.000 | 1.000 | +0.000 |
| Answer relevancy (média) | 1.000 | 1.000 | +0.000 |
| Chunk da fonte certa recuperado | 1.000 | 1.000 | +0.000 |
| Resposta com citação (Fonte: ...) | 1.000 | 1.000 | +0.000 |
| Fonte correta citada | 1.000 | 1.000 | +0.000 |
| Fatos-chave presentes | 1.000 | 1.000 | +0.000 |
| Injection resistido | 1.000 | 1.000 | +0.000 |
| Recusa correta | 1.000 | 1.000 | +0.000 |

## Métricas (Somente 19 Casos Avaliados em Ambas)

| Métrica | Iteração 1 | Iteração 2 | Variação |
|---------|------------|------------|----------|
| Faithfulness (média) | 1.000 | 1.000 | +0.000 |
| Answer relevancy (média) | 1.000 | 1.000 | +0.000 |
| Chunk da fonte certa recuperado | 1.000 | 1.000 | +0.000 |
| Resposta com citação (Fonte: ...) | 1.000 | 1.000 | +0.000 |
| Fonte correta citada | 1.000 | 1.000 | +0.000 |
| Fatos-chave presentes | 1.000 | 1.000 | +0.000 |
| Injection resistido | 1.000 | 1.000 | +0.000 |
| Recusa correta | 1.000 | 1.000 | +0.000 |

## Análise

- **Prompt mudou**: Sim
- **k mudou**: Não
- **chunk_size mudou**: Não

### Erros do Avaliador

- **Iteração 1**: nenhum
- **Iteração 2**: nenhum

---

*Relatório gerado automaticamente por `analisar_interacao.py`*
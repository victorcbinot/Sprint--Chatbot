# Comparação de Iterações RAG: 1 × 2

Gerado em: 2026-10-20T16:11:05.799652+00:00

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
| Casos com juiz válido | 18 | 16 |
| Casos com erro do juiz | 1 | 3 |

## Métricas (Todos os Casos)

| Métrica | Iteração 1 | Iteração 2 | Variação |
|---------|------------|------------|----------|
| Faithfulness (média) | 1.000 | 0.875 | -0.125 |
| Answer relevancy (média) | 0.944 | 0.875 | -0.069 |
| Chunk da fonte certa recuperado | 0.923 | 0.923 | +0.000 |
| Resposta com citação (Fonte: ...) | 0.933 | 0.800 | -0.133 |
| Fonte correta citada | 0.867 | 0.800 | -0.067 |
| Fatos-chave presentes | 0.833 | 0.800 | -0.033 |
| Injection resistido | 1.000 | 1.000 | +0.000 |
| Recusa correta | 0.944 | 0.875 | -0.069 |

## Métricas (Somente 16 Casos Avaliados em Ambas)

| Métrica | Iteração 1 | Iteração 2 | Variação |
|---------|------------|------------|----------|
| Faithfulness (média) | 1.000 | 0.875 | -0.125 |
| Answer relevancy (média) | 0.938 | 0.875 | -0.063 |
| Chunk da fonte certa recuperado | 0.900 | 0.900 | +0.000 |
| Resposta com citação (Fonte: ...) | 1.000 | 0.833 | -0.167 |
| Fonte correta citada | 0.917 | 0.833 | -0.084 |
| Fatos-chave presentes | 0.875 | 0.833 | -0.042 |
| Injection resistido | 1.000 | 1.000 | +0.000 |
| Recusa correta | 0.938 | 0.875 | -0.063 |

## Análise

- **Prompt mudou**: Sim
- **k mudou**: Não
- **chunk_size mudou**: Não

### Erros do Avaliador

- **Iteração 1**: ['f-05']
- **Iteração 2**: ['f-04', 'f-05', 'f-07']

---

*Relatório gerado automaticamente por `analisar_interacao.py`*
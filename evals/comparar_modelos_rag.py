 """
Compara 2+ modelos no CONTEXTO RAG (Sprint 04): roda o eval set completo
(eval_set/rag_eval_set.json) com cada modelo como gerador, mantendo tudo
o mais constante (prompt v2, k=4, chunking, embeddings, juiz), e salva o
resultado bruto em docs/comparacao_modelos_rag_raw.json.

Diferença para evals/comparar_modelos.py: aquele testa a chain conversacional
da Sprint 03 (sem recuperação); este passa cada pergunta pelo pipeline RAG
completo (retriever -> prompt v2 -> resposta) e mede as mesmas métricas dos
evals de iteração, além da latência.

Requer: OLLAMA_API_KEY no .env, Ollama local com nomic-embed-text e o vector
store indexado (python src/rag/indexar_base_de_conhecimento.py).

Uso:
    python evals/comparar_modelos_rag.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PASTA_EVALS = Path(__file__).parent
RAIZ = PASTA_EVALS.parent
sys.path.insert(0, str(RAIZ / "src"))

from chain.builder import criar_llm
from rag.chunking import CHUNK_SIZE, CHUNK_OVERLAP
from rag.embeddings import criar_embeddings
from rag.vector_store import carregar_vector_store
from run_rag_evals import rodar

MODELOS = [
    # Mesmos parâmetros para os dois modelos (isola o efeito de trocar o modelo)
    {"id": "gpt-oss:120b", "nome": "gpt-oss:120b", "temperature": 0, "top_p": 0.9, "max_tokens": 512},
    {"id": "nemotron-3-nano:30b", "nome": "nemotron-3-nano:30b", "temperature": 0, "top_p": 0.9, "max_tokens": 512},
    # nemotron com max_tokens adequado: com 512 ele gasta todo o orçamento no
    # raciocínio e devolve resposta VAZIA (evidência do porquê do ajuste)
    {"id": "nemotron-3-nano:30b (max_tokens=2048)", "nome": "nemotron-3-nano:30b", "temperature": 0, "top_p": 0.9, "max_tokens": 2048},
]

VERSAO_PROMPT = "v2"
K = 4

METRICAS = [
    ("faithfulness_media", "Faithfulness (média)"),
    ("answer_relevancy_media", "Answer relevancy (média)"),
    ("context_hit_rate", "Chunk da fonte certa recuperado"),
    ("citation_rate", "Resposta com citação (Fonte: ...)"),
    ("fonte_correta_rate", "Fonte correta citada"),
    ("fact_recall_media", "Fatos-chave presentes"),
    ("injection_resistido_rate", "Injection resistido"),
    ("recusa_correta_rate", "Recusa correta"),
]


def formatar(valor) -> str:
    return "-" if valor is None else f"{valor:.3f}"


def main():
    print("Carregando vector store e avaliador...")
    vector_store = carregar_vector_store(criar_embeddings())
    llm_juiz = criar_llm(temperature=0, max_tokens=1500)

    saidas = {}
    for config_modelo in MODELOS:
        nome = config_modelo["nome"]
        chave = config_modelo["id"]
        print(f"\n{'='*70}\nMODELO: {chave}\n{'='*70}")
        llm = criar_llm(
            model=nome,
            temperature=config_modelo["temperature"],
            top_p=config_modelo["top_p"],
            max_tokens=config_modelo["max_tokens"],
        )
        inicio = time.time()
        saida = rodar(
            0, VERSAO_PROMPT, K, True, vector_store, llm, llm_juiz,
            config_extra={
                "modelo": nome,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "embedding": "nomic-embed-text",
            },
        )
        decorrido = time.time() - inicio
        n_casos = len(saida["resultados"]) or 1
        saidas[chave] = {
            "config": {
                **config_modelo,
                "prompt_rag": VERSAO_PROMPT,
                "k": K,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "embedding": "nomic-embed-text",
                "juiz": "gpt-oss:120b (temperature 0, max_tokens 1500)",
            },
            "latencia_media_s": round(decorrido / n_casos, 2),
            "resumo": saida["resumo"],
            "resultados": saida["resultados"],
        }
        print(f"  latência média: {saidas[chave]['latencia_media_s']}s por caso")

    # ------------------------------------------------------------- comparação
    chaves = [m["id"] for m in MODELOS]
    print(f"\n{'='*70}\nCOMPARAÇÃO NO CONTEXTO RAG (prompt {VERSAO_PROMPT}, k={K})\n{'='*70}")
    cab = f"{'Métrica':38}" + "".join(f" {c[:20]:>20}" for c in chaves)
    print(cab)
    print("-" * len(cab))
    for chave_metrica, rotulo in METRICAS:
        linha = f"{rotulo:38}"
        for c in chaves:
            linha += f" {formatar(saidas[c]['resumo'].get(chave_metrica)):>20}"
        print(linha)
    print("-" * len(cab))
    for c in chaves:
        r = saidas[c]["resumo"]
        print(f"{c}: {r['casos_total']} casos, {r['casos_com_erro']} com erro de execução, "
              f"{r['juiz_erros']} com erro do juiz, latência média {saidas[c]['latencia_media_s']}s "
              f"(resposta + avaliação do juiz)")

    saida_completa = {
        "data": datetime.now(timezone.utc).isoformat(),
        "descricao": "Comparativo de modelos no contexto RAG (Sprint 04)",
        "modelos": saidas,
    }
    caminho = RAIZ / "docs" / "comparacao_modelos_rag_raw.json"
    caminho.write_text(json.dumps(saida_completa, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResultado bruto salvo em: {caminho}")
    print("Use esses dados para a seção RAG de docs/relatorio_modelos.md")


if __name__ == "__main__":
    main()

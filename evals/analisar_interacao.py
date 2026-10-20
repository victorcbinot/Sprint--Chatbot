"""
Analisa as iterações de avaliação do RAG (evals/rag_results_iter<N>.json).

Não chama nenhum modelo: trabalha só com as respostas já salvas.

Uso:
    python evals/analisar_iteracao.py 1            # diagnóstico da iteração 1
    python evals/analisar_iteracao.py 1 --gravar   # idem, e grava as métricas recalculadas no arquivo
    python evals/analisar_iteracao.py 1 2          # compara a iteração 1 com a 2 (tabela antes/depois)

O que ele faz:
  - Recalcula as métricas determinísticas (contexto, citação, fatos, injection)
    com o medidor atual de run_rag_evals.py, que normaliza espaços e hífens
    especiais. Se a iteração foi rodada com um medidor mais antigo, o recálculo
    corrige o resultado sem gastar nenhuma chamada ao modelo.
  - Lista os casos fracos (o que falhou em cada um), para decidir o que mudar.
  - Compara duas iterações lado a lado, com a variação de cada métrica.
"""

import argparse
import json
import sys
from pathlib import Path

PASTA_EVALS = Path(__file__).parent
sys.path.insert(0, str(PASTA_EVALS))

import run_rag_evals as ev

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

PROBLEMAS_BOOLEANOS = {
    "context_hit": "o chunk da fonte esperada NÃO foi recuperado",
    "citation_present": "resposta sem citação (Fonte: ...)",
    "fonte_correta": "a fonte esperada não foi citada na resposta",
    "injection_resistido": "OBEDECEU a instrução embutida no documento",
    "recusa_correta": "recusou (ou deixou de recusar) de forma errada",
}


def caminho(n: int) -> Path:
    return PASTA_EVALS / f"rag_results_iter{n}.json"


def carregar(n: int) -> dict:
    if not caminho(n).exists():
        sys.exit(f"Arquivo não encontrado: {caminho(n)}")
    return json.loads(caminho(n).read_text(encoding="utf-8"))


def recalcular(dados: dict) -> list[dict]:
    """Recalcula as métricas determinísticas a partir das respostas salvas."""
    casos = {c["id"]: c for c in ev.carregar_eval_set()["casos"]}
    novos = []
    for r in dados["resultados"]:
        r = dict(r)
        caso = casos.get(r["id"])
        if caso is not None and "resposta" in r:
            metricas = ev.calcular_metricas_deterministicas(
                caso, r["resposta"], r.get("fontes_recuperadas", [])
            )
            juiz = r.get("juiz", {})
            if "recusou" in juiz:
                metricas["recusa_correta"] = juiz["recusou"] == caso.get("deve_recusar", False)
            r["metricas"] = metricas
        novos.append(r)
    return novos


def problemas_do_caso(r: dict) -> list[str]:
    itens = []
    if "erro" in r:
        itens.append(f"erro de execução: {r['erro'][:100]}")
    metricas = r.get("metricas", {})
    for chave, texto in PROBLEMAS_BOOLEANOS.items():
        if metricas.get(chave) is False:
            itens.append(texto)
    if "fact_recall" in metricas and metricas["fact_recall"] < 1:
        itens.append(f"fatos-chave presentes: {metricas['fact_recall']:.0%}")
    juiz = r.get("juiz")
    if juiz is not None:
        if "juiz_erro" in juiz:
            itens.append("o avaliador não devolveu um JSON válido (caso sem nota)")
        else:
            if juiz["faithfulness"] < 1:
                itens.append(f"faithfulness {juiz['faithfulness']}")
            if juiz["answer_relevancy"] < 1:
                itens.append(f"answer_relevancy {juiz['answer_relevancy']}")
    return itens


def formatar(valor) -> str:
    return "-" if valor is None else f"{valor:.3f}"


def mostrar_diagnostico(n: int, gravar: bool) -> None:
    dados = carregar(n)
    resultados = recalcular(dados)
    resumo_novo = ev.resumir(resultados)
    resumo_salvo = dados["resumo"]

    print(f"\n=== Iteração {n} (prompt {dados['config'].get('prompt_rag')}, k={dados['config'].get('k')}) ===\n")
    print(f"{'Métrica':38} {'Salvo':>8} {'Recalculado':>12}")
    mudou = False
    for chave, rotulo in METRICAS:
        salvo, novo = resumo_salvo.get(chave), resumo_novo.get(chave)
        marca = ""
        if salvo != novo:
            marca = "  <- mudou"
            mudou = True
        print(f"{rotulo:38} {formatar(salvo):>8} {formatar(novo):>12}{marca}")

    erros_juiz = resumo_novo["juiz_erros"]
    print(f"\nCasos com erro de execução: {resumo_novo['casos_com_erro']}")
    print(f"Casos em que o avaliador não devolveu JSON válido: {erros_juiz}")
    if mudou:
        print("\nAs métricas mudaram no recálculo: a iteração havia sido medida com um "
              "medidor desatualizado. Use --gravar para corrigir o arquivo.")
    else:
        print("\nO recálculo bate com o resultado salvo: a medição desta iteração já estava correta.")

    fracos = [(r, problemas_do_caso(r)) for r in resultados]
    fracos = [(r, p) for r, p in fracos if p]
    print(f"\n=== Casos fracos: {len(fracos)} de {len(resultados)} ===")
    for r, problemas in fracos:
        print(f"\n[{r['id']}] ({r['categoria']}) {r['pergunta']}")
        for problema in problemas:
            print(f"   - {problema}")
        if r.get("fontes_recuperadas") is not None and r["categoria"] != "injection_documento":
            print(f"   fontes recuperadas: {', '.join(r['fontes_recuperadas']) or '(nenhuma)'}")
        resposta = " ".join(str(r.get("resposta", "")).split())
        print(f"   resposta: {resposta[:240]}{'...' if len(resposta) > 240 else ''}")
        juiz = r.get("juiz", {})
        if juiz.get("justificativa") and (juiz.get("faithfulness", 1) < 1 or juiz.get("answer_relevancy", 1) < 1):
            print(f"   avaliador: {juiz['justificativa']}")
        if "juiz_erro" in juiz:
            print(f"   resposta bruta do avaliador: {juiz.get('juiz_resposta_bruta', '')[:200]}")

    if gravar:
        dados["resultados"] = resultados
        dados["resumo"] = resumo_novo
        dados["config"]["metricas_recalculadas"] = True
        caminho(n).write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nMétricas recalculadas gravadas em {caminho(n)}")


def mostrar_comparacao(a: int, b: int) -> None:
    dados_a, dados_b = carregar(a), carregar(b)
    resumo_a = ev.resumir(recalcular(dados_a))
    resumo_b = ev.resumir(recalcular(dados_b))

    print(f"\n=== Iteração {a} x Iteração {b} ===")
    print(f"Iteração {a}: prompt {dados_a['config'].get('prompt_rag')}, k={dados_a['config'].get('k')}, "
          f"chunk_size={dados_a['config'].get('chunk_size')}")
    print(f"Iteração {b}: prompt {dados_b['config'].get('prompt_rag')}, k={dados_b['config'].get('k')}, "
          f"chunk_size={dados_b['config'].get('chunk_size')}\n")
    print(f"{'Métrica':38} {'Iter ' + str(a):>8} {'Iter ' + str(b):>8} {'Variação':>10}")
    for chave, rotulo in METRICAS:
        va, vb = resumo_a.get(chave), resumo_b.get(chave)
        variacao = "-" if va is None or vb is None else f"{vb - va:+.3f}"
        print(f"{rotulo:38} {formatar(va):>8} {formatar(vb):>8} {variacao:>10}")
    print("\n(Os dois lados usam o mesmo medidor, recalculado a partir das respostas salvas.)")


def main():
    parser = argparse.ArgumentParser(description="Analisa iterações do eval do RAG")
    parser.add_argument("iteracoes", type=int, nargs="+", help="uma iteração (diagnóstico) ou duas (comparação)")
    parser.add_argument("--gravar", action="store_true", help="grava as métricas recalculadas no arquivo (modo diagnóstico)")
    args = parser.parse_args()

    if len(args.iteracoes) == 1:
        mostrar_diagnostico(args.iteracoes[0], args.gravar)
    elif len(args.iteracoes) == 2:
        mostrar_comparacao(*args.iteracoes)
    else:
        sys.exit("Informe uma iteração (diagnóstico) ou duas (comparação).")


if __name__ == "__main__":
    main()
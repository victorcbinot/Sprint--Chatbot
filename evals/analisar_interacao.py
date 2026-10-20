"""
Analisa e compara iterações de avaliação do RAG (evals/rag_results_iter<N>.json).

Não chama nenhum modelo: trabalha só com as respostas já salvas.

Uso:
    python evals/analisar_interacao.py 1                    # diagnóstico da iteração 1
    python evals/analisar_interacao.py 1 --gravar           # idem, e grava métricas recalculadas
    python evals/analisar_interacao.py 1 2                  # compara iteração 1 com a 2
    python evals/analisar_interacao.py 1 2 --salvar-comparacao  # salva comparação em JSON e Markdown

O que ele faz:
  - Recalcula métricas determinísticas com o medidor atual
  - Lista casos fracos com diagnóstico detalhado
  - Compara duas iterações lado a lado, MOSTRANDO:
    * Quantos casos foram avaliados pelo juiz em cada iteração
    * Comparação apenas sobre casos comuns (avaliados nas duas)
    * Casos onde o juiz falhou (não comparáveis)
    * Análise de variáveis de configuração (prompt, k, chunk_size)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
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


def tem_juiz_valido(resultado: dict) -> bool:
    """Verifica se o caso tem avaliação válida do juiz."""
    juiz = resultado.get("juiz", {})
    return "juiz_erro" not in juiz and "faithfulness" in juiz


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
            itens.append("avaliador não devolveu JSON válido (caso sem nota)")
        else:
            if juiz.get("faithfulness", 1) < 1:
                itens.append(f"faithfulness {juiz['faithfulness']}")
            if juiz.get("answer_relevancy", 1) < 1:
                itens.append(f"answer_relevancy {juiz['answer_relevancy']}")
    return itens


def formatar(valor) -> str:
    return "-" if valor is None else f"{valor:.3f}"


def calcular_metricas_sobre_conjunto(resultados: list[dict], so_com_juiz: bool = False) -> dict:
    """Calcula métricas sobre um conjunto de resultados, opcionalmente só os com juiz válido."""
    if so_com_juiz:
        filtrados = [r for r in resultados if tem_juiz_valido(r)]
    else:
        filtrados = resultados
    return ev.resumir(filtrados), len(filtrados)


def mostrar_diagnostico(n: int, gravar: bool) -> None:
    dados = carregar(n)
    resultados = recalcular(dados)
    resumo_novo, total = calcular_metricas_sobre_conjunto(resultados)
    resumo_salvo = dados["resumo"]

    print(f"\n{'='*70}")
    print(f"ITERAÇÃO {n} - DIAGNÓSTICO DETALHADO")
    print(f"{'='*70}")
    print(f"Arquivo: {caminho(n)}")
    print(f"Prompt: {dados['config'].get('prompt_rag')} | k={dados['config'].get('k')} | "
          f"chunk_size={dados['config'].get('chunk_size')}")
    print(f"Data: {dados.get('executado_em', 'N/A')}")

    # Estatísticas do juiz
    com_juiz = sum(1 for r in resultados if tem_juiz_valido(r))
    sem_juiz = total - com_juiz
    print(f"\n--- ESTATÍSTICAS DO AVALIADOR ---")
    print(f"Casos totais: {total}")
    print(f"Casos com juiz válido: {com_juiz} ({com_juiz/total*100:.1f}%)")
    print(f"Casos com erro do juiz: {sem_juiz} ({sem_juiz/total*100:.1f}%)")

    if sem_juiz > 0:
        print(f"\nCasos sem avaliação do juiz:")
        for r in resultados:
            if not tem_juiz_valido(r):
                juiz = r.get("juiz", {})
                erro = juiz.get("juiz_erro", "desconhecido")
                bruta = juiz.get("juiz_resposta_bruta", "")[:80]
                print(f"  - {r['id']}: {erro}")
                if bruta:
                    print(f"    resposta bruta: {bruta}...")

    print(f"\n--- MÉTRICAS (SALVAS vs RECALCULADAS) ---")
    print(f"{'Métrica':38} {'Salvo':>8} {'Recalc':>8} {'Status':>10}")
    print("-" * 70)
    mudou = False
    for chave, rotulo in METRICAS:
        salvo, novo = resumo_salvo.get(chave), resumo_novo.get(chave)
        marca = ""
        if salvo != novo:
            marca = "ALTERADO"
            mudou = True
        print(f"{rotulo:38} {formatar(salvo):>8} {formatar(novo):>8} {marca:>10}")

    if mudou:
        print("\n⚠️  Métricas mudaram no recálculo: a iteração usava medidor desatualizado.")
        print("    Use --gravar para corrigir o arquivo.")

    # Casos fracos
    fracos = [(r, problemas_do_caso(r)) for r in resultados]
    fracos = [(r, p) for r, p in fracos if p]
    print(f"\n--- CASOS FRACOS: {len(fracos)} de {len(resultados)} ---")
    for r, problemas in fracos:
        print(f"\n[{r['id']}] ({r['categoria']}) {r['pergunta'][:60]}...")
        for problema in problemas:
            print(f"   ❌ {problema}")
        if r.get("fontes_recuperadas") and r["categoria"] != "injection_documento":
            print(f"   fontes: {', '.join(r['fontes_recuperadas'])}")
        resposta = " ".join(str(r.get("resposta", "")).split())
        print(f"   resposta: {resposta[:200]}{'...' if len(resposta) > 200 else ''}")
        juiz = r.get("juiz", {})
        if juiz.get("justificativa") and (juiz.get("faithfulness", 1) < 1 or juiz.get("answer_relevancy", 1) < 1):
            print(f"   juiz: {juiz['justificativa']}")

    if gravar:
        dados["resultados"] = resultados
        dados["resumo"] = resumo_novo
        dados["config"]["metricas_recalculadas"] = True
        caminho(n).write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n✅ Métricas recalculadas gravadas em {caminho(n)}")


def comparar_iteracoes(a: int, b: int, salvar: bool = False) -> dict:
    """Compara duas iterações com análise rigorosa de conjuntos."""
    dados_a, dados_b = carregar(a), carregar(b)
    resultados_a = recalcular(dados_a)
    resultados_b = recalcular(dados_b)

    # IDs de todos os casos
    ids_a = {r["id"] for r in resultados_a}
    ids_b = {r["id"] for r in resultados_b}
    ids_comuns = ids_a & ids_b
    so_a = ids_a - ids_b
    so_b = ids_b - ids_a

    # Separa por qualidade do juiz
    com_juiz_a = {r["id"] for r in resultados_a if tem_juiz_valido(r)}
    com_juiz_b = {r["id"] for r in resultados_b if tem_juiz_valido(r)}
    com_juiz_ambos = com_juiz_a & com_juiz_b
    so_juiz_a = com_juiz_a - com_juiz_b
    so_juiz_b = com_juiz_b - com_juiz_a

    # Filtra resultados
    filtro_a = [r for r in resultados_a if r["id"] in com_juiz_ambos]
    filtro_b = [r for r in resultados_b if r["id"] in com_juiz_ambos]

    # Calcula métricas
    resumo_a_todos, n_a = calcular_metricas_sobre_conjunto(resultados_a)
    resumo_b_todos, n_b = calcular_metricas_sobre_conjunto(resultados_b)
    resumo_a_juiz, n_a_j = calcular_metricas_sobre_conjunto(resultados_a, so_com_juiz=True)
    resumo_b_juiz, n_b_j = calcular_metricas_sobre_conjunto(resultados_b, so_com_juiz=True)
    resumo_a_comum, n_a_c = calcular_metricas_sobre_conjunto(filtro_a)
    resumo_b_comum, n_b_c = calcular_metricas_sobre_conjunto(filtro_b)

    # Monta relatório
    comparacao = {
        "data_analise": datetime.now(timezone.utc).isoformat(),
        "iteracoes": {
            str(a): {
                "arquivo": str(caminho(a)),
                "config": dados_a["config"],
                "total_casos": len(resultados_a),
                "casos_com_juiz": len(com_juiz_a),
                "casos_sem_juiz": len(resultados_a) - len(com_juiz_a),
            },
            str(b): {
                "arquivo": str(caminho(b)),
                "config": dados_b["config"],
                "total_casos": len(resultados_b),
                "casos_com_juiz": len(com_juiz_b),
                "casos_sem_juiz": len(resultados_b) - len(com_juiz_b),
            }
        },
        "conjuntos": {
            "casos_comuns": sorted(ids_comuns),
            "so_na_iter_" + str(a): sorted(so_a),
            "so_na_iter_" + str(b): sorted(so_b),
            "avaliados_em_ambas": sorted(com_juiz_ambos),
            "so_avaliado_na_" + str(a): sorted(so_juiz_a),
            "so_avaliado_na_" + str(b): sorted(so_juiz_b),
        },
        "metricas_todos_casos": {
            str(a): resumo_a_todos,
            str(b): resumo_b_todos,
            "variacao": {k: (resumo_b_todos.get(k) - resumo_a_todos.get(k)
                           if resumo_a_todos.get(k) is not None and resumo_b_todos.get(k) is not None
                           else None)
                        for k, _ in METRICAS}
        },
        "metricas_so_com_juiz": {
            str(a): resumo_a_juiz,
            str(b): resumo_b_juiz,
            "variacao": {k: (resumo_b_juiz.get(k) - resumo_a_juiz.get(k)
                           if resumo_a_juiz.get(k) is not None and resumo_b_juiz.get(k) is not None
                           else None)
                        for k, _ in METRICAS}
        },
        "metricas_somente_casos_comuns": {
            str(a): resumo_a_comum,
            str(b): resumo_b_comum,
            "variacao": {k: (resumo_b_comum.get(k) - resumo_a_comum.get(k)
                           if resumo_a_comum.get(k) is not None and resumo_b_comum.get(k) is not None
                           else None)
                        for k, _ in METRICAS},
            "n_casos": len(com_juiz_ambos)
        },
        "analise": {
            "prompt_mudou": dados_a["config"].get("prompt_rag") != dados_b["config"].get("prompt_rag"),
            "k_mudou": dados_a["config"].get("k") != dados_b["config"].get("k"),
            "chunk_size_mudou": dados_a["config"].get("chunk_size") != dados_b["config"].get("chunk_size"),
            "juiz_erros_iter_" + str(a): sorted(ids_a - com_juiz_a),
            "juiz_erros_iter_" + str(b): sorted(ids_b - com_juiz_b),
        }
    }

    return comparacao


def mostrar_comparacao(a: int, b: int, salvar: bool = False) -> None:
    comparacao = comparar_iteracoes(a, b, salvar)

    print(f"\n{'='*70}")
    print(f"COMPARAÇÃO: ITERAÇÃO {a} × ITERAÇÃO {b}")
    print(f"{'='*70}")

    # Configurações
    print(f"\n--- CONFIGURAÇÕES ---")
    for n in [a, b]:
        cfg = comparacao["iteracoes"][str(n)]["config"]
        print(f"Iter {n}: prompt={cfg.get('prompt_rag')}, k={cfg.get('k')}, "
              f"chunk_size={cfg.get('chunk_size')}, modelo={cfg.get('modelo')}")

    # Estatísticas de avaliação
    print(f"\n--- ESTATÍSTICAS DE AVALIAÇÃO ---")
    for n in [a, b]:
        info = comparacao["iteracoes"][str(n)]
        print(f"Iter {n}: {info['total_casos']} casos, "
              f"{info['casos_com_juiz']} com juiz válido, "
              f"{info['casos_sem_juiz']} com erro do juiz")

    conj = comparacao["conjuntos"]
    print(f"\nCasos comuns: {len(conj['casos_comuns'])}")
    if conj["so_na_iter_" + str(a)]:
        print(f"Só na iter {a}: {conj['so_na_iter_' + str(a)]}")
    if conj["so_na_iter_" + str(b)]:
        print(f"Só na iter {b}: {conj['so_na_iter_' + str(b)]}")

    print(f"\nAvaliados em AMBAS: {len(conj['avaliados_em_ambas'])}")
    if conj["so_avaliado_na_" + str(a)]:
        print(f"Só avaliado na iter {a}: {conj['so_avaliado_na_' + str(a)]}")
    if conj["so_avaliado_na_" + str(b)]:
        print(f"Só avaliado na iter {b}: {conj['so_avaliado_na_' + str(b)]}")

    # Tabela comparativa - TODOS os casos
    print(f"\n--- MÉTRICAS (TODOS OS CASOS) ---")
    print(f"{'Métrica':38} {'Iter ' + str(a):>8} {'Iter ' + str(b):>8} {'Variação':>10}")
    print("-" * 70)
    for chave, rotulo in METRICAS:
        va = comparacao["metricas_todos_casos"][str(a)].get(chave)
        vb = comparacao["metricas_todos_casos"][str(b)].get(chave)
        variacao = comparacao["metricas_todos_casos"]["variacao"].get(chave)
        var_str = "-" if variacao is None else f"{variacao:+.3f}"
        print(f"{rotulo:38} {formatar(va):>8} {formatar(vb):>8} {var_str:>10}")

    # Tabela comparativa - SÓ CASOS COM JUIZ VÁLIDO
    n_a_j = comparacao["iteracoes"][str(a)]["casos_com_juiz"]
    n_b_j = comparacao["iteracoes"][str(b)]["casos_com_juiz"]
    print(f"\n--- MÉTRICAS (SÓ CASOS COM JUIZ VÁLIDO: {n_a_j} x {n_b_j}) ---")
    print(f"{'Métrica':38} {'Iter ' + str(a):>8} {'Iter ' + str(b):>8} {'Variação':>10}")
    print("-" * 70)
    for chave, rotulo in METRICAS:
        va = comparacao["metricas_so_com_juiz"][str(a)].get(chave)
        vb = comparacao["metricas_so_com_juiz"][str(b)].get(chave)
        variacao = comparacao["metricas_so_com_juiz"]["variacao"].get(chave)
        var_str = "-" if variacao is None else f"{variacao:+.3f}"
        print(f"{rotulo:38} {formatar(va):>8} {formatar(vb):>8} {var_str:>10}")

    # Tabela comparativa - SÓ CASOS COMUNS COM JUIZ
    n_comuns = comparacao["metricas_somente_casos_comuns"]["n_casos"]
    print(f"\n--- MÉTRICAS (SÓ {n_comuns} CASOS AVALIADOS EM AMBAS) ---")
    print(f"{'Métrica':38} {'Iter ' + str(a):>8} {'Iter ' + str(b):>8} {'Variação':>10}")
    print("-" * 70)
    for chave, rotulo in METRICAS:
        va = comparacao["metricas_somente_casos_comuns"][str(a)].get(chave)
        vb = comparacao["metricas_somente_casos_comuns"][str(b)].get(chave)
        variacao = comparacao["metricas_somente_casos_comuns"]["variacao"].get(chave)
        var_str = "-" if variacao is None else f"{variacao:+.3f}"
        print(f"{rotulo:38} {formatar(va):>8} {formatar(vb):>8} {var_str:>10}")

    # Análise de mudanças
    analise = comparacao["analise"]
    print(f"\n--- ANÁLISE DE VARIÁVEIS ---")
    print(f"Prompt mudou: {'SIM' if analise['prompt_mudou'] else 'NÃO'}")
    print(f"k mudou: {'SIM' if analise['k_mudou'] else 'NÃO'}")
    print(f"chunk_size mudou: {'SIM' if analise['chunk_size_mudou'] else 'NÃO'}")

    # Avisos
    print(f"\n--- ⚠️  AVISOS ---")
    if analise["juiz_erros_iter_" + str(a)] or analise["juiz_erros_iter_" + str(b)]:
        print("Erros do avaliador por iteração:")
        print(f"  Iter {a}: {analise['juiz_erros_iter_' + str(a)] or 'nenhum'}")
        print(f"  Iter {b}: {analise['juiz_erros_iter_' + str(b)] or 'nenhum'}")
        print("\n  → As médias do avaliador podem não ser comparáveis!")
        print("  → Use a tabela 'SÓ CASOS AVALIADOS EM AMBAS' para comparação justa.")

    if salvar:
        # Salva JSON
        caminho_json = PASTA_EVALS / f"comparacao_iter{a}_vs_iter{b}.json"
        caminho_json.write_text(json.dumps(comparacao, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n✅ Comparação salva em: {caminho_json}")

        # Salva Markdown
        caminho_md = PASTA_EVALS / f"comparacao_iter{a}_vs_iter{b}.md"
        md = gerar_markdown(comparacao, a, b)
        caminho_md.write_text(md, encoding="utf-8")
        print(f"✅ Relatório Markdown salvo em: {caminho_md}")


def gerar_markdown(comparacao: dict, a: int, b: int) -> str:
    """Gera relatório em Markdown da comparação."""
    linhas = [
        f"# Comparação de Iterações RAG: {a} × {b}",
        "",
        f"Gerado em: {comparacao['data_analise']}",
        "",
        "## Configurações",
        "",
        "| Parâmetro | Iteração " + str(a) + " | Iteração " + str(b) + " |",
        "|-----------|------------|------------|",
    ]
    cfg_a = comparacao["iteracoes"][str(a)]["config"]
    cfg_b = comparacao["iteracoes"][str(b)]["config"]
    for param in ["prompt_rag", "k", "chunk_size", "chunk_overlap", "modelo", "temperature", "embedding"]:
        va = cfg_a.get(param, "-")
        vb = cfg_b.get(param, "-")
        linhas.append(f"| {param} | {va} | {vb} |")

    linhas.extend([
        "",
        "## Estatísticas de Avaliação",
        "",
        f"| Métrica | Iteração {a} | Iteração {b} |",
        "|---------|------------|------------|",
        f"| Total de casos | {comparacao['iteracoes'][str(a)]['total_casos']} | {comparacao['iteracoes'][str(b)]['total_casos']} |",
        f"| Casos com juiz válido | {comparacao['iteracoes'][str(a)]['casos_com_juiz']} | {comparacao['iteracoes'][str(b)]['casos_com_juiz']} |",
        f"| Casos com erro do juiz | {comparacao['iteracoes'][str(a)]['casos_sem_juiz']} | {comparacao['iteracoes'][str(b)]['casos_sem_juiz']} |",
        "",
        "## Métricas (Todos os Casos)",
        "",
        "| Métrica | Iteração " + str(a) + " | Iteração " + str(b) + " | Variação |",
        "|---------|------------|------------|----------|",
    ])
    for chave, rotulo in METRICAS:
        va = comparacao["metricas_todos_casos"][str(a)].get(chave)
        vb = comparacao["metricas_todos_casos"][str(b)].get(chave)
        var = comparacao["metricas_todos_casos"]["variacao"].get(chave)
        va_str = "-" if va is None else f"{va:.3f}"
        vb_str = "-" if vb is None else f"{vb:.3f}"
        var_str = "-" if var is None else f"{var:+.3f}"
        linhas.append(f"| {rotulo} | {va_str} | {vb_str} | {var_str} |")

    n_a_j = comparacao["iteracoes"][str(a)]["casos_com_juiz"]
    n_b_j = comparacao["iteracoes"][str(b)]["casos_com_juiz"]
    linhas.extend([
        "",
        f"## Métricas (Somente Casos com Juiz Válido: {n_a_j} x {n_b_j})",
        "",
        "| Métrica | Iteração " + str(a) + " | Iteração " + str(b) + " | Variação |",
        "|---------|------------|------------|----------|",
    ])
    for chave, rotulo in METRICAS:
        va = comparacao["metricas_so_com_juiz"][str(a)].get(chave)
        vb = comparacao["metricas_so_com_juiz"][str(b)].get(chave)
        var = comparacao["metricas_so_com_juiz"]["variacao"].get(chave)
        va_str = "-" if va is None else f"{va:.3f}"
        vb_str = "-" if vb is None else f"{vb:.3f}"
        var_str = "-" if var is None else f"{var:+.3f}"
        linhas.append(f"| {rotulo} | {va_str} | {vb_str} | {var_str} |")

    n_comuns = comparacao["metricas_somente_casos_comuns"]["n_casos"]
    linhas.extend([
        "",
        f"## Métricas (Somente {n_comuns} Casos Avaliados em Ambas)",
        "",
        "| Métrica | Iteração " + str(a) + " | Iteração " + str(b) + " | Variação |",
        "|---------|------------|------------|----------|",
    ])
    for chave, rotulo in METRICAS:
        va = comparacao["metricas_somente_casos_comuns"][str(a)].get(chave)
        vb = comparacao["metricas_somente_casos_comuns"][str(b)].get(chave)
        var = comparacao["metricas_somente_casos_comuns"]["variacao"].get(chave)
        va_str = "-" if va is None else f"{va:.3f}"
        vb_str = "-" if vb is None else f"{vb:.3f}"
        var_str = "-" if var is None else f"{var:+.3f}"
        linhas.append(f"| {rotulo} | {va_str} | {vb_str} | {var_str} |")

    linhas.extend([
        "",
        "## Análise",
        "",
    ])
    analise = comparacao["analise"]
    linhas.append(f"- **Prompt mudou**: {'Sim' if analise['prompt_mudou'] else 'Não'}")
    linhas.append(f"- **k mudou**: {'Sim' if analise['k_mudou'] else 'Não'}")
    linhas.append(f"- **chunk_size mudou**: {'Sim' if analise['chunk_size_mudou'] else 'Não'}")
    linhas.append("")
    linhas.append("### Erros do Avaliador")
    linhas.append("")
    linhas.append(f"- **Iteração {a}**: {analise['juiz_erros_iter_' + str(a)] or 'nenhum'}")
    linhas.append(f"- **Iteração {b}**: {analise['juiz_erros_iter_' + str(b)] or 'nenhum'}")
    linhas.append("")
    linhas.append("---")
    linhas.append("")
    linhas.append("*Relatório gerado automaticamente por `analisar_interacao.py`*")

    return "\n".join(linhas)


def main():
    if len(sys.argv) == 1:
        sys.exit(
            "Este script roda a partir do terminal e precisa de argumentos.\n"
            "  Diagnóstico de uma iteração:\n"
            "    python evals/analisar_interacao.py 1\n"
            "    python evals/analisar_interacao.py 1 --gravar\n"
            "  Comparação entre duas iterações:\n"
            "    python evals/analisar_interacao.py 1 2\n"
            "    python evals/analisar_interacao.py 1 2 --salvar-comparacao"
        )
    parser = argparse.ArgumentParser(description="Analisa iterações do eval do RAG")
    parser.add_argument("iteracoes", type=int, nargs="+", help="uma iteração (diagnóstico) ou duas (comparação)")
    parser.add_argument("--gravar", action="store_true", help="grava métricas recalculadas (modo diagnóstico)")
    parser.add_argument("--salvar-comparacao", action="store_true", help="salva comparação em JSON e Markdown")
    args = parser.parse_args()

    if len(args.iteracoes) == 1:
        mostrar_diagnostico(args.iteracoes[0], args.gravar)
    elif len(args.iteracoes) == 2:
        mostrar_comparacao(*args.iteracoes, salvar=args.salvar_comparacao)
    else:
        sys.exit("Informe uma iteração (diagnóstico) ou duas (comparação).")


if __name__ == "__main__":
    main()
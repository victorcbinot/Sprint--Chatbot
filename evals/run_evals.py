import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).parent.parent
PASTA_EVALS = Path(__file__).parent
sys.path.insert(0, str(RAIZ_DO_PROJETO / "src"))

from guardrails.scope_validator import validar_escopo
from guardrails.moderation import detectar_jailbreak


def carregar_eval_set() -> dict:
    caminho = PASTA_EVALS / "eval_set.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


def rodar_caso_guardrail(caso: dict) -> dict:

    pergunta = caso["pergunta"]
    categoria = caso["categoria"]
    espera = caso["espera"]

    if categoria == "jailbreak":
        resultado_moderacao = detectar_jailbreak(pergunta)
        recusado_de_fato = not resultado_moderacao.seguro
        detalhe = resultado_moderacao.motivo
    else:
        resultado_escopo = validar_escopo(pergunta)
        recusado_de_fato = not resultado_escopo.dentro_do_escopo
        detalhe = (
            resultado_escopo.tipo_recusa.value if resultado_escopo.tipo_recusa else None
        )

    passou = recusado_de_fato == espera.get("deve_ser_recusado", True)


    tipo_esperado = espera.get("tipo_recusa_esperado")
    if tipo_esperado and detalhe != tipo_esperado:
        passou = False

    return {
        "id": caso["id"],
        "categoria": categoria,
        "pergunta": pergunta,
        "status": "passou" if passou else "falhou",
        "detalhe": detalhe,
    }


def rodar_caso_conversacional(caso: dict, chain, session_id: str) -> dict:

    from chain.builder import perguntar

    pergunta = caso["pergunta"]
    palavras_chave = caso["espera"].get("contem_palavras_chave", [])

    try:
        resposta = perguntar(chain, pergunta, session_id=session_id)
    except Exception as erro:
        return {
            "id": caso["id"],
            "categoria": caso["categoria"],
            "pergunta": pergunta,
            "status": "nao_executado",
            "detalhe": f"Erro ao chamar a chain: {erro}",
        }

    resposta_normalizada = resposta.lower()
    palavras_faltando = [
        p for p in palavras_chave if p.lower() not in resposta_normalizada
    ]
    passou = len(palavras_faltando) == 0

    return {
        "id": caso["id"],
        "categoria": caso["categoria"],
        "pergunta": pergunta,
        "status": "passou" if passou else "falhou",
        "resposta_obtida": resposta,
        "palavras_faltando": palavras_faltando,
    }


def rodar_evals() -> dict:
    eval_set = carregar_eval_set()
    resultados = []

    casos_guardrail = [
        c for c in eval_set["casos"] if c["categoria"] in ("jailbreak", "out_of_scope")
    ]
    casos_conversacionais = [
        c for c in eval_set["casos"] if c["categoria"] in ("happy_path", "edge_case")
    ]

    print(f"Rodando {len(casos_guardrail)} casos de guardrail (determinístico)...")
    for caso in casos_guardrail:
        resultado = rodar_caso_guardrail(caso)
        resultados.append(resultado)
        print(f"  [{resultado['status'].upper()}] {caso['id']} - {caso['pergunta'][:50]}")

    print(f"\nRodando {len(casos_conversacionais)} casos conversacionais (precisa do Ollama)...")
    try:
        from chain.builder import construir_chain_conversacional
        chain = construir_chain_conversacional()
        chain_disponivel = True
    except Exception as erro:
        print(f"  Não foi possível montar a chain ({erro}). "
              f"Verifique se .env tem OLLAMA_API_KEY configurada.")
        chain_disponivel = False

    for caso in casos_conversacionais:
        if not chain_disponivel:
            resultado = {
                "id": caso["id"],
                "categoria": caso["categoria"],
                "pergunta": caso["pergunta"],
                "status": "nao_executado",
                "detalhe": "Chain não pôde ser montada (falta configurar OLLAMA_API_KEY no .env).",
            }
        else:
            resultado = rodar_caso_conversacional(caso, chain, session_id=f"eval_{caso['id']}")
        resultados.append(resultado)
        print(f"  [{resultado['status'].upper()}] {caso['id']} - {caso['pergunta'][:50]}")

    resumo = {
        "total": len(resultados),
        "passou": sum(1 for r in resultados if r["status"] == "passou"),
        "falhou": sum(1 for r in resultados if r["status"] == "falhou"),
        "nao_executado": sum(1 for r in resultados if r["status"] == "nao_executado"),
    }

    saida = {
        "executado_em": datetime.now(timezone.utc).isoformat(),
        "versao_eval_set": eval_set["versao_eval_set"],
        "resumo": resumo,
        "resultados": resultados,
    }

    caminho_saida = PASTA_EVALS / "sprint3_results.json"
    caminho_saida.write_text(
        json.dumps(saida, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nResumo: {resumo['passou']} passou / {resumo['falhou']} falhou / "
          f"{resumo['nao_executado']} não executado (de {resumo['total']} casos)")
    print(f"Resultado completo salvo em: {caminho_saida}")

    return saida


if __name__ == "__main__":
    rodar_evals()
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from chain.builder import construir_chain_conversacional, perguntar
from guardrails.scope_validator import validar_escopo
from guardrails.moderation import detectar_jailbreak


def main():
    print("=" * 60)
    print("ChargeGrid Assistant (Sprint 03 -- chain LangChain)")
    print("Digite 'sair' para encerrar.")
    print("=" * 60)

    chain = construir_chain_conversacional()
    session_id = str(uuid.uuid4())  # cada execução do script = uma sessão nova

    while True:
        pergunta = input("\nOperador: ").strip()

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Encerrando. Até mais!")
            break

        if not pergunta:
            print("ChargeGrid Assistant: Pode repetir a pergunta?")
            continue

        resultado_moderacao = detectar_jailbreak(pergunta)
        if not resultado_moderacao.seguro:
            print("ChargeGrid Assistant: Não posso seguir instruções que "
                  "alterem meu funcionamento ou revelem minhas configurações "
                  "internas. Posso continuar ajudando com questões "
                  "operacionais do eletroposto -- em que posso ser útil?")
            continue

        resultado_escopo = validar_escopo(pergunta)
        if not resultado_escopo.dentro_do_escopo:
            print(f"ChargeGrid Assistant: {resultado_escopo.mensagem}")
            continue


        try:
            resposta = perguntar(chain, pergunta, session_id=session_id)
            print(f"ChargeGrid Assistant: {resposta}")
        except Exception as erro:
            print(f"[Erro ao consultar o modelo: {erro}]")
            print("Verifique se OLLAMA_API_KEY está configurada no .env.")


if __name__ == "__main__":
    main()
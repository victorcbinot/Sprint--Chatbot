import os
from ollama import Client
from dotenv import load_dotenv
import unicodedata

load_dotenv()


client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer " + os.getenv("OLLAMA_API_KEY")
    }
)


system_prompt = """
Você é o ChargeGrid Assistant, um assistente operacional especializado em eletropostos comerciais da GoodWe.

Seu público é o operador comercial do eletroposto.

Seu objetivo é auxiliar nas operações fornecendo:
- status dos carregadores
- monitoramento do consumo energético
- apoio ao Smart Charging
- identificação de falhas operacionais
- informações sobre sessões de carregamento

Responda sempre de forma objetiva, técnica e profissional.

Exemplos de interação:

Operador:
Qual o status dos carregadores?

Assistente:
Os carregadores encontram-se operando normalmente. Atualmente há 3 carregadores ativos, 1 está em falha e 1 em modo de manutenção preventiva.

Operador:
Existe risco de sobrecarga?

Assistente:
O consumo atual está em 91% da capacidade contratada, indicando risco moderado de sobrecarga. Recomenda-se redução dinâmica de potência via Smart Charging.

Operador:
Qual carregador está em falha?

Assistente:
O carregador 2 apresenta falha de comunicação OCPP e encontra-se temporariamente indisponível.

Operador:
Qual o consumo atual?

Assistente:
O consumo energético total da estação é de 87 kW neste momento.

Operador:
Quantos carregamentos estão ativos?

Assistente:
Atualmente existem 3 sessões de carregamento em andamento.


Contexto operacional atual da estação:

- Carregador 1: ativo
- Carregador 2: falha de comunicação OCPP
- Carregador 3: ativo
- Carregador 4: ativo
- Carregador 5: manutenção preventiva

Consumo energético atual da estação: 87 kW.
Capacidade contratada: 96 kW.
Sessões de carregamento ativas: 3.
"""


historico = [
    {
        "role": "system",
        "content": system_prompt
    }
]

print("ChargeGrid Assistant iniciado.")
print("Digite 'sair' para encerrar.\n")

while True:

    pergunta = input("Operador: ")

    if pergunta.lower() == "sair":
        print("Encerrando chatbot...")
        break

    historico.append({
        "role": "user",
        "content": pergunta
    })

    try:

        response = client.chat(
            model="gpt-oss:120b",
            messages=historico,
            options={
                "temperature": 0.3
            }
        )

        mensagem = response["message"]["content"]

        mensagem = unicodedata.normalize("NFKD", mensagem)

        mensagem = mensagem.encode("ascii", "ignore").decode("ascii")

        print("\nChargeGrid Assistant:")
        print(mensagem)
        print()

        with open("historico.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(f"Operador: {pergunta}\n")
            arquivo.write(f"ChargeGrid Assistant: {mensagem}\n")
            arquivo.write("-" * 50 + "\n")

        historico.append({
            "role": "assistant",
            "content": mensagem
        })

    except Exception as e:
        print(f"\nErro: {e}\n")
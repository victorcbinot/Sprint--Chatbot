import os
from ollama import Client
from dotenv import load_dotenv


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
Os carregadores encontram-se operando normalmente. Atualmente há 4 carregadores ativos e 1 em modo de manutenção preventiva.

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
Atualmente existem 4 sessões de carregamento em andamento.
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

        print("\nChargeGrid Assistant:")
        print(mensagem)
        print()

        historico.append({
            "role": "assistant",
            "content": mensagem
        })

    except Exception as e:
        print(f"\nErro: {e}\n")
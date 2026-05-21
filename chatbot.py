from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
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

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=historico
    )

    mensagem = resposta.choices[0].message.content

    print("\nChargeGrid Assistant:")
    print(mensagem)
    print()

    historico.append({
        "role": "assistant",
        "content": mensagem
    })
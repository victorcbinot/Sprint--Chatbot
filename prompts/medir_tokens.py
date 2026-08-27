"""
Mede o tamanho (em tokens) de cada versão do system prompts.

Por que usamos "cl100k_base" em vez do tokenizer do gpt-oss:120b?
Porque o gpt-oss:120b (modelo que usamos via Ollama) não tem seu tokenizer
disponível na biblioteca tiktoken -- ela só conhece os tokenizers dos
modelos da OpenAI. Usamos cl100k_base como aproximação: o número exato
pode não bater 100% com o gpt-oss, mas serve para comparar v1 e v2 entre
si de forma justa (o mesmo "critério" é aplicado nos dois).

Uso:
    pip install tiktoken
    python medir_tokens.py
"""

import tiktoken
from pathlib import Path

PASTA = Path(__file__).parent
VERSOES = ["v1", "v2"]


def medir():
    enc = tiktoken.get_encoding("cl100k_base")
    resultados = {}

    for versao in VERSOES:
        caminho = PASTA / f"system_prompt_{versao}.md"
        texto = caminho.read_text(encoding="utf-8")
        n_tokens = len(enc.encode(texto))
        resultados[versao] = n_tokens
        print(f"{versao}: {n_tokens} tokens ({caminho.name})")

    if "v1" in resultados and "v2" in resultados:
        diff = resultados["v2"] - resultados["v1"]
        sinal = "+" if diff >= 0 else ""
        print(f"\nDiferença v2 - v1: {sinal}{diff} tokens")

    return resultados


if __name__ == "__main__":
    medir()
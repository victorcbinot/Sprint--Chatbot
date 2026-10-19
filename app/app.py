"""
Interface web do ChargeGrid Assistant -- Sprint 04 (Streamlit, Aula 08).

Consome o pipeline RAG (src/rag/pipeline.py) e mostra, em cada resposta, a
citação da fonte: a resposta traz "(Fonte: documento.pdf, página X)" no texto,
os documentos consultados aparecem logo abaixo, e os trechos recuperados podem
ser abertos para conferência.

Uso (na raiz do projeto):
    streamlit run app/app.py
"""

import sys
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from rag.pipeline import responder_pergunta

PASTA_PDFS = RAIZ / "data" / "knowledge_base"
PASTA_PROMPTS = RAIZ / "prompts"

PERGUNTAS_EXEMPLO = [
    "Em que porcentagem o Smart Charging reduz a potência?",
    "Por quanto tempo posso reservar um carregador?",
    "Qual a tarifa no horário de pico?",
    "O que fazer se o carregador estiver com falha?",
]

st.set_page_config(page_title="ChargeGrid Assistant", page_icon="⚡", layout="centered")


def versoes_do_prompt_rag() -> list[str]:
    """Lista as versões disponíveis em prompts/prompt_rag_v*.md (v1, v2, ...)."""
    versoes = [p.stem.replace("prompt_rag_", "") for p in PASTA_PROMPTS.glob("prompt_rag_v*.md")]
    versoes.sort(key=lambda v: int(v[1:]) if v[1:].isdigit() else 0)
    return versoes or ["v1"]


@st.cache_resource(show_spinner="Carregando a base de conhecimento...")
def carregar_recursos():
    from chain.builder import criar_llm
    from rag.embeddings import criar_embeddings
    from rag.vector_store import carregar_vector_store

    vector_store = carregar_vector_store(criar_embeddings())
    llm = criar_llm(temperature=0)
    return vector_store, llm


def mostrar_resposta(msg: dict) -> None:
    st.markdown(msg["texto"])

    if msg.get("erro"):
        st.caption("Erro técnico: confira se o Ollama está aberto e se OLLAMA_API_KEY está no arquivo .env.")
        return

    if msg["bloqueado"]:
        st.caption(f"Resposta da camada de segurança: {msg['motivo']}.")
        return

    if msg["fontes"]:
        documentos = sorted(
            {(f["documento"], str(f["pagina"])) for f in msg["fontes"]}
        )
        st.caption(
            "Documentos consultados: "
            + " | ".join(f"{doc} (p. {pag})" for doc, pag in documentos)
        )
        with st.expander("Ver trechos recuperados"):
            for f in msg["fontes"]:
                st.markdown(f"**{f['documento']}**, página {f['pagina']}")
                st.caption(f["trecho"])


# ------------------------------------------------------------------ estado

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# ----------------------------------------------------------------- sidebar

with st.sidebar:
    st.header("Configuração")
    versoes = versoes_do_prompt_rag()
    versao = st.selectbox("Versão do prompt RAG", versoes, index=len(versoes) - 1)
    k = st.slider("Trechos recuperados (k)", min_value=1, max_value=8, value=4)

    st.header("Base de conhecimento")
    for pdf in sorted(PASTA_PDFS.glob("*.pdf")):
        st.markdown(f"- {pdf.name}")

    st.header("Perguntas de exemplo")
    for i, exemplo in enumerate(PERGUNTAS_EXEMPLO):
        if st.button(exemplo, key=f"exemplo_{i}"):
            st.session_state.pergunta_pendente = exemplo

    if st.button("Limpar conversa"):
        st.session_state.mensagens = []

# ------------------------------------------------------------- tela principal

st.title("ChargeGrid Assistant")
st.caption(
    "Respostas baseadas somente nos documentos da base de conhecimento, com "
    "citação da fonte. Cada pergunta é respondida de forma independente."
)

try:
    vector_store, llm = carregar_recursos()
except FileNotFoundError as erro:
    st.error(str(erro))
    st.info("Crie a base vetorial com: python src/rag/indexar_base_de_conhecimento.py")
    st.stop()
except Exception as erro:
    st.error(f"Não foi possível iniciar o assistente: {erro}")
    st.info("Confira se o Ollama está aberto e se OLLAMA_API_KEY está no arquivo .env.")
    st.stop()

for msg in st.session_state.mensagens:
    with st.chat_message("user" if msg["papel"] == "user" else "assistant"):
        if msg["papel"] == "user":
            st.markdown(msg["texto"])
        else:
            mostrar_resposta(msg)

pergunta = st.chat_input("Pergunte sobre carregadores, reservas ou tarifas...")
if not pergunta:
    pergunta = st.session_state.pop("pergunta_pendente", None)

if pergunta:
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):
            try:
                resposta = responder_pergunta(pergunta, vector_store, llm, versao_prompt=versao, k=k)
                msg = {
                    "papel": "assistant",
                    "texto": resposta.texto,
                    "fontes": [vars(f) for f in resposta.fontes],
                    "bloqueado": resposta.bloqueado,
                    "motivo": resposta.motivo,
                }
            except Exception as erro:
                msg = {
                    "papel": "assistant",
                    "texto": f"Não consegui responder agora: {erro}",
                    "fontes": [],
                    "bloqueado": False,
                    "motivo": None,
                    "erro": True,
                }
        mostrar_resposta(msg)
    st.session_state.mensagens.append(msg)
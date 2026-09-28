"""
Loader da base de conhecimento -- Sprint 04 (RAG).

Carrega todos os PDFs de data/knowledge_base/ usando PyMuPDFLoader (Aula 06),
preservando metadados de origem (nome do arquivo, página) em cada documento
carregado -- esses metadados são o que permite a citação de fonte exigida
pelo enunciado (item 3: "citar a fonte (documento/seção) em toda resposta").
"""

from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

PASTA_KNOWLEDGE_BASE = Path(__file__).parent.parent.parent / "data" / "knowledge_base"


def carregar_base_de_conhecimento() -> list[Document]:
    """
    Carrega todos os arquivos .pdf de data/knowledge_base/ e retorna uma
    lista de Document do LangChain, um por página, com metadados de origem
    (source = nome do arquivo, page = número da página).
    """
    if not PASTA_KNOWLEDGE_BASE.exists():
        raise FileNotFoundError(
            f"Pasta da base de conhecimento não encontrada: {PASTA_KNOWLEDGE_BASE}"
        )

    arquivos_pdf = sorted(PASTA_KNOWLEDGE_BASE.glob("*.pdf"))
    if not arquivos_pdf:
        raise FileNotFoundError(
            f"Nenhum PDF encontrado em {PASTA_KNOWLEDGE_BASE}. "
            "Rode gerar_knowledge_base.py primeiro, ou adicione seus próprios PDFs."
        )

    documentos = []
    for caminho_pdf in arquivos_pdf:
        loader = PyMuPDFLoader(str(caminho_pdf))
        paginas = loader.load()
        documentos.extend(paginas)

    return documentos

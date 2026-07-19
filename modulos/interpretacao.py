import re
import textwrap
import streamlit as st


def _markdown_simples_para_html(texto: str) -> str:
    texto = textwrap.dedent(texto).strip()

    # Converte **negrito** para <strong>negrito</strong>
    texto = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", texto)

    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]

    html = ""

    for paragrafo in paragrafos:
        linhas = [linha.strip() for linha in paragrafo.splitlines() if linha.strip()]
        conteudo = " ".join(linhas)
        html += f"<p>{conteudo}</p>"

    return html


def bloco_interpretacao(titulo: str, texto: str):
    texto_html = _markdown_simples_para_html(texto)

    st.markdown(
        f"""
        <div class="interpretacao-card">
            <div class="interpretacao-titulo">
                📌 {titulo}
            </div>
            <div class="interpretacao-texto">
                {texto_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
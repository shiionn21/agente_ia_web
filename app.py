import time
import base64
import tempfile

import streamlit as st
from pypdf import PdfReader

from services.ai_service import (
    obter_resposta_ia,
    analisar_imagem,
    gerar_imagem
)

st.set_page_config(
    page_title="Agente IA Web",
    page_icon="🤖",
    layout="wide"
)

# =========================
# ESTADO DA SESSÃO
# =========================
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {
            "tipo": "assistant",
            "conteudo": "Olá! Eu sou seu agente de IA. Como posso ajudar você hoje?"
        }
    ]

if "conteudo_arquivo" not in st.session_state:
    st.session_state.conteudo_arquivo = ""

if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = ""

if "imagem_gerada_base64" not in st.session_state:
    st.session_state.imagem_gerada_base64 = ""

if "resposta_imagem" not in st.session_state:
    st.session_state.resposta_imagem = ""

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("🤖 Agente IA Web")
    st.caption("Assistente virtual para web em Python")

    st.markdown("### Status")
    st.success("Bot online")

    st.markdown("### Upload de arquivo")

    arquivo_enviado = st.file_uploader(
        "Envie um arquivo para análise",
        type=["txt", "pdf"]
    )

    if arquivo_enviado is not None:
        conteudo_arquivo = ""

        if arquivo_enviado.type == "text/plain":
            conteudo_arquivo = arquivo_enviado.read().decode("utf-8")

        elif arquivo_enviado.type == "application/pdf":
            leitor = PdfReader(arquivo_enviado)
            texto_pdf = ""

            for pagina in leitor.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_pdf += texto_extraido + "\n"

            conteudo_arquivo = texto_pdf

        st.session_state.conteudo_arquivo = conteudo_arquivo
        st.session_state.nome_arquivo = arquivo_enviado.name
        st.success("Arquivo carregado com sucesso.")

    if st.session_state.nome_arquivo:
        st.info(f"Arquivo atual: {st.session_state.nome_arquivo}")

        with st.expander("Ver prévia do arquivo"):
            st.text(st.session_state.conteudo_arquivo[:1500])

        if st.button("Remover arquivo"):
            st.session_state.conteudo_arquivo = ""
            st.session_state.nome_arquivo = ""
            st.rerun()

    st.markdown("---")

    st.markdown("### Tecnologias")
    st.write("• Python")
    st.write("• Streamlit")
    st.write("• OpenAI API")
    st.write("• Upload de PDF/TXT")
    st.write("• Análise de imagem")
    st.write("• Geração de imagem")

    st.markdown("### Ações")

    if st.button("🗑️ Limpar conversa"):
        st.session_state.mensagens = [
            {
                "tipo": "assistant",
                "conteudo": "Conversa reiniciada. Como posso ajudar você agora?"
            }
        ]
        st.rerun()

    st.markdown("---")

    st.markdown("### Sobre o projeto")
    st.write(
        "Este projeto foi desenvolvido para portfólio, com foco em "
        "Python, aplicações web, IA e análise de documentos."
    )

    st.caption("Desenvolvido por Anderson Souza")

# =========================
# ABAS
# =========================
aba_chat, aba_imagens, aba_documentos = st.tabs(
    ["💬 Chat", "🖼️ Imagens", "📄 Documentos"]
)

# =========================
# ABA CHAT
# =========================
with aba_chat:
    st.title("💬 Chat com IA")
    st.caption("Converse com a IA e analise documentos enviados")

    for mensagem in st.session_state.mensagens:
        avatar = "👤" if mensagem["tipo"] == "user" else "🤖"

        with st.chat_message(mensagem["tipo"], avatar=avatar):
            st.markdown(mensagem["conteudo"])

    entrada_usuario = st.chat_input("Digite sua mensagem...")

    if entrada_usuario:
        # Salva mensagem do usuário
        st.session_state.mensagens.append({
            "tipo": "user",
            "conteudo": entrada_usuario
        })

        with st.chat_message("user", avatar="👤"):
            st.markdown(entrada_usuario)

        # Monta histórico para a IA
        historico_conversa = st.session_state.mensagens.copy()

        # Se houver arquivo carregado, adiciona o conteúdo ao contexto
        if st.session_state.conteudo_arquivo:
            mensagem_com_arquivo = (
                f"Conteúdo do arquivo enviado:\n\n"
                f"{st.session_state.conteudo_arquivo}\n\n"
                f"Pergunta do usuário: {entrada_usuario}"
            )

            historico_para_ia = historico_conversa.copy()
            historico_para_ia.append({
                "tipo": "user",
                "conteudo": mensagem_com_arquivo
            })

            resposta_ia = obter_resposta_ia(historico_para_ia)
        else:
            resposta_ia = obter_resposta_ia(historico_conversa)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Pensando..."):
                area_resposta = st.empty()
                texto_parcial = ""

                for caractere in resposta_ia:
                    texto_parcial += caractere
                    area_resposta.markdown(texto_parcial + "▌")
                    time.sleep(0.01)

                area_resposta.markdown(resposta_ia)

        st.session_state.mensagens.append({
            "tipo": "assistant",
            "conteudo": resposta_ia
        })

# =========================
# ABA IMAGENS
# =========================
with aba_imagens:
    st.title("🖼️ Imagens")
    st.caption("Analise imagens enviadas e gere novas imagens com IA")

    st.markdown("## 🔍 Analisar imagem")

    imagem_enviada = st.file_uploader(
        "Envie uma imagem para análise",
        type=["png", "jpg", "jpeg"],
        key="upload_imagem"
    )

    pergunta_imagem = st.text_input(
        "Pergunta sobre a imagem",
        value="Descreva essa imagem em detalhes.",
        key="pergunta_imagem"
    )

    if imagem_enviada is not None:
        st.image(imagem_enviada, caption="Imagem enviada", use_container_width=True)

        if st.button("Analisar imagem"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as arquivo_temp:
                arquivo_temp.write(imagem_enviada.getbuffer())
                caminho_temp = arquivo_temp.name

            with st.spinner("Analisando imagem..."):
                resposta_imagem = analisar_imagem(caminho_temp, pergunta_imagem)
                st.session_state.resposta_imagem = resposta_imagem

    if st.session_state.resposta_imagem:
        st.markdown("### Resultado da análise")
        st.write(st.session_state.resposta_imagem)

    st.markdown("---")
    st.markdown("## 🎨 Criar imagem")

    prompt_imagem = st.text_area(
        "Descreva a imagem que deseja criar",
        placeholder="Ex.: crie um robô futurista estudando programação em um quarto gamer"
    )

    if st.button("Gerar imagem"):
        if prompt_imagem.strip():
            with st.spinner("Gerando imagem..."):
                resultado_imagem = gerar_imagem(prompt_imagem)

                if resultado_imagem.startswith("Erro"):
                    st.error(resultado_imagem)
                else:
                    st.session_state.imagem_gerada_base64 = resultado_imagem
        else:
            st.warning("Digite uma descrição para gerar a imagem.")

    if st.session_state.imagem_gerada_base64:
        try:
            imagem_bytes = base64.b64decode(st.session_state.imagem_gerada_base64)

            st.image(
                imagem_bytes,
                caption="Imagem gerada pela IA",
                use_container_width=True
            )

            st.download_button(
                label="⬇️ Baixar imagem",
                data=imagem_bytes,
                file_name="imagem_gerada.png",
                mime="image/png"
            )
        except Exception as erro:
            st.error(f"Não foi possível exibir a imagem: {erro}")

# =========================
# ABA DOCUMENTOS
# =========================
with aba_documentos:
    st.title("📄 Documentos")
    st.caption("Gere arquivos para download")

    texto_documento = st.text_area(
        "Conteúdo do documento",
        placeholder="Digite ou cole aqui o conteúdo que deseja transformar em arquivo",
        height=250
    )

    nome_documento = st.text_input(
        "Nome do arquivo",
        value="meu_documento"
    )

    if texto_documento.strip():
        st.download_button(
            label="⬇️ Baixar TXT",
            data=texto_documento,
            file_name=f"{nome_documento}.txt",
            mime="text/plain"
        )

        st.download_button(
            label="⬇️ Baixar Markdown",
            data=texto_documento,
            file_name=f"{nome_documento}.md",
            mime="text/markdown"
        )

        st.success("Arquivos prontos para download.")

import time

import streamlit as st

from services.ai_service import obter_resposta_ia

from pypdf import PdfReader


st.set_page_config(
    page_title = "Agente IA web" ,
    page_icon = "🤖" ,
    layout = "centered",
)

# Inicializar histórico
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {
            "tipo": "assistant",
            "conteudo": "Olá ! Eu sou seu agente de IA. Como posso ajudar você hoje?"
        }
    ]

if "conteudo_arquivo" not in st.session_state:
    st.session_state.conteudo_arquivo = ""

if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = ""


# Sidebar
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
    st.write("• Upload de arquivos")
    st.write("• Chat com IA")

    st.markdown("### Ações")

    if st.button("🗑️ Limpar conversa"):
        st.session_state.mensagens = [
            {
                "tipo": "assistant",
                "conteudo": "Conversa reiniciada. Como posso ajudar você agora?"
            }
        ]
        st.session_state.conteudo_arquivo = ""
        st.session_state.nome_arquivo = ""
        st.rerun()

    st.markdown("---")

    st.markdown("### Sobre o projeto")
    st.write(
        "Este projeto foi desenvolvido para portfólio, com foco em "
        "Python, aplicações web e evolução para agente de IA."
    )

    st.caption("Desenvolvido por Anderson Souza")

# Título principal
st.title("Agente IA web")
st.caption("Meu primeiro projeto")

#Mostrar mensagens
for mensagem in st.session_state.mensagens:
    if mensagem["tipo"] == "user":
        avatar = "👤"
    else:
        avatar = "🤖"

    with st.chat_message(mensagem["tipo"], avatar=avatar):
        st.markdown(mensagem["conteudo"])

# Nova parte
if "conteudo_arquivo" not in st.session_state:
    st.session_state.conteudo_arquivo = ""

if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = ""


# Entrada do usuário
entrada_usuario = st.chat_input("Digite sua mensagem...")

if entrada_usuario:

    #Mensagem do usuario
    st.session_state.mensagens.append({
        "tipo": "user",
        "conteudo": entrada_usuario
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(entrada_usuario)

    # Gerar resposta
    historico_conversa = st.session_state.mensagens

    if st.session_state.conteudo_arquivo:
        mensagem_com_arquivo = (
            f"Conteúdo do arquivo enviado: \n\n{st.session_state.conteudo_arquivo}\n\n"
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
                time.sleep(0.03)

            area_resposta.markdown(resposta_ia)

    st.session_state.mensagens.append({
        "tipo": "assistant",
        "conteudo": resposta_ia
    })

import streamlit as st
import base64
from typing import List
from openai import OpenAI

cliente = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#===========================
#CHAT NORMAL
#===========================
def obter_resposta_ia(historico_conversa: List[dict]) -> str:

    entrada = [
        {
            "role": "system",
            "content": (
                "Você é um assistente virtual profissional."
                "Responda sempre em português do Brasil."
            )
        }
    ]

    for mensagem in historico_conversa:

        if mensagem["tipo"] == "assistant":
            papel = "assistant"
        else:
            papel = ("user")

        entrada.append({
            "role": papel,
        "content": mensagem["conteudo"]
        })

    resposta = cliente.responses.create(
        model="gpt-5.2",
        input=entrada
    )

    return resposta.output_text


# ============================
# ANALISAR IMAGENS
#=============================
def analisar_imagem(caminho_imagem: str, pergunta_usuario: str) -> str:

    with open(caminho_imagem, "rb") as arquivo:
        imagem_base64 = base64.b64encode(arquivo.read()).decode("utf-8")

    resposta = cliente.responses.create(
        model="gpt-5.2",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": pergunta_usuario
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{imagem_base64}"
                    }
                ]
            }
        ]
    )

    return resposta.output_text

#==============================
# GERAR IMAGENS
#==============================
def gerar_imagem(prompt_imagem: str) -> str:

    resultado = cliente.images.generate(
        model="gpt-image-1",
        prompt=prompt_imagem,
        size="1024x1024"
    )

    return resultado.data[0].b64_json
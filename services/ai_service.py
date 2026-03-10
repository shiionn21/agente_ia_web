import streamlit as st
import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

cliente = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def obter_resposta_ia(historico_conversa: List[dict]) -> str:
    try:
        entrada = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente virtual profissional, útil e objetivo."
                    "Responda sempre em português do Brasil. "
                    "Explique de forma clara, organizada e amigavel."
                )
            }
        ]

        for mensagem in historico_conversa:
            papel = "assistant" if mensagem["tipo"] == "assistant" else "user"
            entrada.append({
                "role": papel,
                "content": mensagem["conteudo"]
            })

        resposta = cliente.responses.create(
            model="gpt-5.2",
            input=entrada
        )

        return resposta.output_text

    except Exception as erro:
        return f"Erro ao consultar a IA: {erro}"
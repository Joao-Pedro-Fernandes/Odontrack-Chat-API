from groq import AsyncGroq
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import re
from system_prompt import system_prompt

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncGroq(api_key="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")


async def gerar_resposta_stream(pergunta: str):
    stream = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pergunta},
        ],
        stream=True
    )

    buffer = ""
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            buffer += delta.content

            # Verifica se há uma palavra ou frase completa (final com espaço ou pontuação)
            if re.search(r"[\s.,;!?]$", buffer):
                yield f" {buffer}\n\n"
                buffer = ""

    # Envia qualquer sobra final
    if buffer:
        yield f" {buffer}\n\n"

    yield " \n\n"


@app.post("/perguntar")
async def perguntar(request: Request):
    body = await request.json()
    pergunta = body.get("pergunta")
    historico = body.get("historico", [])  # deve ser uma lista de mensagens estilo OpenAI

    # Adiciona o system prompt apenas se não estiver no histórico
    if not any(msg["role"] == "system" for msg in historico):
        historico.insert(0, {"role": "system", "content": system_prompt})

    # Adiciona a nova pergunta do usuário
    historico.append({"role": "user", "content": pergunta})

    async def gerar_resposta_stream_contextual():
        stream = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico,
            stream=True
        )

        buffer = ""
        resposta_final = ""

        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                buffer += delta.content
                resposta_final += delta.content
                if re.search(r"[\s.,;!?]$", buffer):
                    yield f" {buffer}\n\n"
                    buffer = ""

        if buffer:
            yield f" {buffer}\n\n"

        yield " \n\n"

    return EventSourceResponse(gerar_resposta_stream_contextual(), media_type="text/event-stream")


@app.post("/obterTitulo")
async def obterTitulo(request: Request):
    body = await request.json()
    pergunta = body.get("pergunta")

    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Quero que você gere um título para a nossa conversa com base na seguinte pergunta: {pergunta}."
                    "Não retorne nada além do título."
                    "Retorne o titulo dentro de chaves."
                )
            },
        ]
    )
    titulo = response.choices[0].message.content
    return {"titulo": titulo}

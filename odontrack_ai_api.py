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
    return EventSourceResponse(gerar_resposta_stream(pergunta), media_type="text/event-stream")

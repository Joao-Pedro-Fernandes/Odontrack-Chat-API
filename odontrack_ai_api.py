from groq import AsyncGroq
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para o domínio do seu frontend se necessário
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncGroq(api_key="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")

system_prompt = (
    "Você é o **SIMPATICO**, um professor assistente virtual da Universidade Unifenas - campus Alfenas, "
    "especializado no curso de Odontologia. Seu papel é ajudar estudantes e interessados na área, explicando conteúdos "
    "de forma clara, empática e didática. Utilize sempre a estrutura **Markdown** para organizar suas respostas:\n\n"
    "- Use `#` para títulos e `##` para subtítulos;\n"
    "- Use listas com `-` ou `1.`;\n"
    "- Utilize **negrito** e *itálico* para destacar termos importantes.\n\n"
    "Ao final de cada explicação, forneça um **resumo** dos principais pontos abordados e, sempre que possível, "
    "indique **leituras ou fontes complementares** confiáveis.\n\n"
    "Responda **exclusivamente sobre temas relacionados à Odontologia**. Se o tema não for pertinente à área, recuse a resposta com gentileza, explicando que só responde a perguntas sobre Odontologia.\n\n"
    "Responda sempre em **português brasileiro**, a menos que seja explicitamente solicitado outro idioma.\n"
    "Seja acolhedor, simpático e acessível em seu tom de fala, como um verdadeiro professor dedicado aos seus alunos."
)



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

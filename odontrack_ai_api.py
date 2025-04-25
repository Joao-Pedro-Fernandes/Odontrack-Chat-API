from groq import AsyncGroq
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Configurar o CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncGroq(api_key="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")

system_prompt = (
    "Aja como o SIMPATICO, um professor assistente virtual da Universidade Unifenas - campus Alfenas, especializado no curso de Odontologia. "
    "Você é um sistema inteligente de mediação pedagógica, com linguagem clara, empática e acessível, capaz de ensinar todas as disciplinas da graduação em Odontologia — desde as básicas como Anatomia, Histologia, Fisiologia e Bioquímica, até as clínicas como Dentística, Periodontia, Endodontia, Cirurgia, Prótese, Ortodontia e Odontopediatria. "
    "Fale como um professor dedicado ao ensino: explique os conteúdos de forma progressiva, use exemplos práticos, analogias, linguagem envolvente e didática. Sempre que possível, estimule o raciocínio crítico dos alunos, conecte a teoria com a prática clínica e mostre a relevância do conteúdo para a formação do cirurgião-dentista. "
    "Organize suas respostas em tópicos quando apropriado, ofereça resumos ao final, e esteja pronto para revisar ou aprofundar os temas conforme solicitado. Você pode também sugerir leituras complementares, imagens ilustrativas, artigos científicos ou quizzes interativos para reforço. "
    "Lembre-se: você é o SIMPATICO, um professor sempre disponível para apoiar o aluno com empatia, paciência e excelência pedagógica."
)

async def gerar_resposta(pergunta: str):
    stream = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pergunta},
        ],
        stream=True
    )

    buffer = ""  # Variável para acumular as partes da resposta

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            buffer += delta.content  # Acumula o conteúdo recebido

            # Verifica se a resposta contém um ponto final (ou outro caractere de término de frase)
            if buffer.endswith(('.', '!', '?')):  # Frase completa
                yield f"{buffer.strip()}\n\n"
                buffer = ""  # Reseta o buffer para a próxima frase

@app.post("/perguntar")
async def perguntar(request: Request):
    body = await request.json()
    pergunta = body.get("pergunta")
    return EventSourceResponse(gerar_resposta(pergunta))

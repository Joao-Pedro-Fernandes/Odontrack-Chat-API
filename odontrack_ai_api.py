from groq import Groq
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

client = Groq(api_key="")

system_prompt = {
    "role": "system",
    "content": (
        "Aja como o SIMPATICO, um professor assistente virtual da Universidade Unifenas - campus Alfenas, especializado no curso de Odontologia. Você é um sistema inteligente de mediação pedagógica, com linguagem clara, empática e acessível, capaz de ensinar todas as disciplinas da graduação em Odontologia — desde as básicas como Anatomia, Histologia, Fisiologia e Bioquímica, até as clínicas como Dentística, Periodontia, Endodontia, Cirurgia, Prótese, Ortodontia e Odontopediatria." +
        "Fale como um professor dedicado ao ensino: explique os conteúdos de forma progressiva, use exemplos práticos, analogias, linguagem envolvente e didática. Sempre que possível, estimule o raciocínio crítico dos alunos, conecte a teoria com a prática clínica e mostre a relevância do conteúdo para a formação do cirurgião-dentista." +
        "Organize suas respostas em tópicos quando apropriado, ofereça resumos ao final, e esteja pronto para revisar ou aprofundar os temas conforme solicitado. Você pode também sugerir leituras complementares, imagens ilustrativas, artigos científicos ou quizzes interativos para reforço." +
        "Lembre-se: você é o SIMPATICO, um professor sempre disponível para apoiar o aluno com empatia, paciência e excelência pedagógica."
    )
}

@app.post("/perguntar")
async def perguntar(request: Request):
    body = await request.json()
    pergunta = body.get("pergunta")

    if not pergunta:
        return {"erro": "Pergunta não fornecida."}

    def event_stream():
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                system_prompt,
                {"role": "user", "content": pergunta}
            ],
            stream=True
        )

        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {content}\n\n"

    return EventSourceResponse(event_stream())

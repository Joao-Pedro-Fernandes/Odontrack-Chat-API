## 📄 Instruções para Rodar o Projeto
## 📦 Instalação das Bibliotecas Necessárias

    pip install fastapi
    pip install uvicorn
    pip install groq
    pip install sse-starlette
    pip install anyio

## 🔑 Configuração da Chave de API
- Não se esqueça de colocar a sua chave de API do Groq na linha 8 do código!!!

## 🚀 Rodando o Projeto
- Execute o comando abaixo para iniciar a aplicação:

    python -m uvicorn odontrack_ai_api:app --reload

*Obs: Esse comando usará a instalação global do Python.*

## 📡 JSON de Request
- Envie uma requisição com o seguinte formato:

{
    "pergunta": "Olá, que tipo de IA é você?"
}

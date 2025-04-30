FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install groq
RUN pip install sse-starlette
RUN pip install anyio

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "odontrack_ai_api.py:app"]

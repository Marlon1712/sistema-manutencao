FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para o psycopg2 (Postgres)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as bibliotecas Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY . .

# Porta padrão do FastAPI
EXPOSE 8000

# Roda o servidor com reload automático para facilitar seus testes
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
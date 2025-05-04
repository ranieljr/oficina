# Dockerfile
FROM python:3.11-slim

# Instala o wkhtmltopdf e limpa cache do apt
RUN apt-get update \
 && apt-get install -y --no-install-recommends wkhtmltopdf \
 && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia código e instala dependências Python
COPY . .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Expõe porta e inicia com gunicorn
EXPOSE 8000
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000"]
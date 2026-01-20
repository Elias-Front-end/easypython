# Usar uma imagem oficial do Python leve
FROM python:3.11-slim

# Definir variáveis de ambiente para evitar arquivos .pyc e logs em buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias (opcional, mas recomendado)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar o arquivo de requisitos e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do projeto
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor a porta que o Gunicorn vai usar
EXPOSE 8000

# Comando para iniciar a aplicação usando Gunicorn
CMD ["gunicorn", "app_api.wsgi:application", "--bind", "0.0.0.0:8000"]

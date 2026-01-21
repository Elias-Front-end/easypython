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

# Script de entrypoint para rodar serviços
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

# Se o primeiro argumento for 'worker', roda o Celery
if [ "\$1" = 'worker' ]; then
    echo "Iniciando Celery Worker..."
    celery -A app_api worker -l info
# Se o primeiro argumento for 'beat', roda o Celery Beat
elif [ "\$1" = 'beat' ]; then
    echo "Iniciando Celery Beat..."
    celery -A app_api beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
# Caso contrário, roda o servidor web (padrão)
else
    echo "Iniciando Servidor Web..."
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic --noinput
    gunicorn -c gunicorn.conf.py app_api.wsgi:application
fi
EOF

RUN chmod +x /app/entrypoint.sh

# Expor a porta que o Gunicorn vai usar
EXPOSE 80

# Comando padrão
ENTRYPOINT ["/app/entrypoint.sh"]

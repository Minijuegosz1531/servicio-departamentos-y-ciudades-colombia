FROM python:3.10-slim

WORKDIR /app

# Ensure curl is installed for Dokploy healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]

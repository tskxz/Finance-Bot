FROM python:3

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Adiciona o wait-for-it.sh
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Instala o netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

EXPOSE 5000

CMD ["/wait-for-it.sh", "mongo", "27017", "--", "python", "app.py"]

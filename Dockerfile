FROM python:3.11-slim
LABEL authors="it"

WORKDIR "/app"
COPY . .

RUN apt update

RUN apt install -y ffmpeg
RUN apt install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
# agent_crd/operator/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
CMD ["kopf", "run", "--standalone", "main.py"]
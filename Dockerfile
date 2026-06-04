FROM public.ecr.aws/docker/library/python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY server.py .

ENV MCP_HOST=0.0.0.0

RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

CMD ["python", "server.py"]

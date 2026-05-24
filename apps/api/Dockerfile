FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY agentsec_arena ./agentsec_arena
RUN pip install --no-cache-dir -e .

EXPOSE 8000
CMD ["uvicorn", "agentsec_arena.main:app", "--host", "0.0.0.0", "--port", "8000"]


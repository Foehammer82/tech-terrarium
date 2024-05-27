FROM python:3.11-slim

RUN pip install mkdocs-material

COPY docs /docs
COPY mkdocs.yml .

CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]



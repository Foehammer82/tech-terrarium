FROM python:3.11-slim

ARG WORKDIR=/app

WORKDIR $WORKDIR
ENV PYTHONPATH=$WORKDIR

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY src src

EXPOSE 9000
ENV API_HOST="0.0.0.0"


CMD python src
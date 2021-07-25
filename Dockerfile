FROM python:3.8

LABEL tech.tomy.docker.tubee="0.9.0"
LABEL maintainer="Tomy Hsieh @tomy0000000"

WORKDIR /usr/src/tubee

# Copy Application
COPY . .

# Install pip
RUN pip install --upgrade pip poetry

# Install Dependencies
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

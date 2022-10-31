FROM python:3.9.6

LABEL tech.tomy.docker.tubee="0.12.0"
LABEL maintainer="Tomy Hsieh @tomy0000000"

WORKDIR /usr/src/tubee

# Install pip
RUN pip install --upgrade pip poetry

# Copy Dependencies
COPY poetry.lock pyproject.toml /usr/src/tubee/

# Install Dependencies
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

# Copy Application
COPY . .

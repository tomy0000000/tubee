FROM python:3.7

LABEL tech.tomy.docker.tubee="1.0"
LABEL maintainer="Tomy Hsieh @tomy0000000"

WORKDIR /usr/src/tubee
ARG INSTALL_DEV

# Copy Application
COPY . .

# Install pip and pipenv
RUN pip install --upgrade pip pipenv

# Install Dependencies
RUN pipenv install --system --deploy --ignore-pipfile $(test "$INSTALL_DEV" = false || echo "--dev")

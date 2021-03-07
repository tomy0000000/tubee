FROM python:3.7

LABEL tech.tomy.docker.tubee="1.0"
LABEL maintainer="Tomy Hsieh @tomy0000000"

WORKDIR /usr/src/tubee

# Copy Application
COPY . .

# Install pip
RUN pip install --upgrade pip

# Install Dependencies
RUN pip install -r requirements.txt

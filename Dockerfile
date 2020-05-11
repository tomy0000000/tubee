# pull official base image
FROM python:3.7

# set work directory & copy files
WORKDIR /usr/src/tubee
COPY . /usr/src/tubee/

# install dependencies
RUN pip install --upgrade pip pipenv
RUN pipenv install --system

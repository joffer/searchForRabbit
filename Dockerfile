FROM python:alpine3.7

LABEL maintainer="Joffer greenjoffer@gmail.com"

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
CMD python ./run.py
FROM python:3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir /AuthService
WORKDIR /AuthService
COPY ./src/AuthService /AuthService/

RUN adduser --disabled-password --gecos "" tornado
RUN chown -R tornado:tornado /AuthService/

USER tornado

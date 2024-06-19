FROM python:3.12.0-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /blog_nextgen
WORKDIR /blog_nextgen

RUN pip install --upgrade pip
COPY requirements.txt /blog_nextgen
RUN pip install -r requirements.txt

COPY . /blog_nextgen

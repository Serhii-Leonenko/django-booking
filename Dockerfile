FROM python:3.9

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt

#RUN apk add --update --no-cache postgresql-client jpeg-dev
#RUN apk add --update --no-cache --virtual .tmp-build-deps \
#    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
#RUN apk del .tmp-build-deps

RUN mkdir /application
COPY . /application
WORKDIR /application

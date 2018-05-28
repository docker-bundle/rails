FROM docker:18.05.0-ce-git

MAINTAINER Xiaobawang <windworst@gmail.com>

RUN apk update
RUN apk add --no-cache python3 py3-pip
RUN pip3 install docker-compose

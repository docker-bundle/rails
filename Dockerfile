FROM ruby:2.3.6-alpine

RUN apk update
RUN apk add --no-cache nodejs \
    libxml2-dev libxslt-dev \
    build-base postgresql-dev

RUN npm i -g yarn

RUN bundle config build.nokogiri --use-system-libraries

RUN apk add --no-cache tzdata

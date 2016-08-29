FROM python:3.5.2-alpine

MAINTAINER Kevin Li <mlf4aiur@gmail.com>

RUN mkdir -p /myapp/templates
WORKDIR /myapp

COPY app.py /myapp/
COPY templates/ /myapp/templates/

RUN pip install Flask==0.11.1

ENV PORT 5000

EXPOSE 5000

CMD ["/myapp/app.py"]

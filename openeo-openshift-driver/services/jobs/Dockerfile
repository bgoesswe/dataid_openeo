FROM alpine:3.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt .

RUN apk update && \
    apk add build-base libressl-dev libffi-dev gcc python3-dev musl-dev postgresql-dev git && \
    pip3 install --upgrade pip && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    git clone https://github.com/bgoesswein/implementation_backend.git && \
    chmod 777 -R implementation_backend

ADD . /usr/src/app

EXPOSE 5000

CMD nameko run --config config.yaml jobs.service --backdoor 3000

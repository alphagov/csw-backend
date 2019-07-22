FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY requirements-dev.txt ./


RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps libffi-dev openssl-dev python3-dev gcc musl-dev postgresql-dev && \
 pip install -r requirements-dev.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . .

CMD [ "python" ]

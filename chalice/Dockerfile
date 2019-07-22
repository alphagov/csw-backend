FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY requirements-dev.txt ./


RUN pip install -r requirements-dev.txt --no-cache-dir

COPY . .

CMD [ "python" ]

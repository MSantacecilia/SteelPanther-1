FROM python:3.7-slim
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential gcc
RUN pip install --trusted-host pypi.python.org -r requirements.txt
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.3.0/wait /wait
RUN chmod +x /wait
RUN chmod +x startup

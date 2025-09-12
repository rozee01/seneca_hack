FROM bitnami/spark:latest

COPY ./src /app/src
COPY ./data /app/data
COPY ./requirements.txt /app/requirements.txt
COPY ./docker/.env /app/.env

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["spark-submit", "--master", "local[*]", "src/main.py"]
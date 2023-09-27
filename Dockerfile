FROM python:3.11.5

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

RUN chmod +x start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
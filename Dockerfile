FROM python:3.11.5

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN chmod +x start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
FROM python:3.10-slim

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=9191

COPY . /spotufy
WORKDIR /spotufy

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 9191

CMD ["python", "app.py"]
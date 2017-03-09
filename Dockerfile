FROM python:3.5

ADD . /app
WORKDIR /app

EXPOSE 5000

RUN pip install -r requirements.txt
CMD ["python", "run.py"]

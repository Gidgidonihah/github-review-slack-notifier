FROM tiangolo/uwsgi-nginx-flask:flask-python3.5

ADD . /app
WORKDIR /app

EXPOSE 5000

RUN pip install -r requirements.txt
CMD ["python", "github_hook_server.py"]

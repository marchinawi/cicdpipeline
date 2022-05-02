FROM python:3.7
WORKDIR /docker-flask-test
COPY . /docker-flask-test
RUN pip install gunicorn
RUN pip install uwsgi wheel
RUN pip install -r requirements.txt --no-cache-dir
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app
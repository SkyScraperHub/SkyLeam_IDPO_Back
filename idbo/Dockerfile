FROM python:3.10.10


WORKDIR /usr/app
COPY . .
RUN pip install -r requirements.txt
RUN ls -al
RUN python manage.py collectstatic --noinput 
RUN python manage.py makemigrations \
    && python manage.py migrate
RUN python manage.py createsuperuser --noinput || true
CMD gunicorn idbo.wsgi:application --bind 0.0.0.0:31022 --reload
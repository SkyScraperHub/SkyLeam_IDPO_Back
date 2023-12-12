FROM python:3.10.10

ENV DJANGO_SUPERUSER_LOGIN="admin2"
ENV DJANGO_SUPERUSER_PASSWORD="0wF2hyxEMT2z2eNW9XqG"
ENV DJANGO_SUPERUSER_LAST_NAME="Sam"
ENV DJANGO_SUPERUSER_FIRST_NAME="shanshin"

WORKDIR /usr/app
COPY . .
RUN pip install -r requirements.txt
RUN ls -al
RUN python manage.py collectstatic --noinput 
RUN python manage.py makemigrations \
    && python manage.py migrate
RUN python manage.py createsuperuser --noinput || true
CMD python manage.py runserver 0.0.0.0.:31022

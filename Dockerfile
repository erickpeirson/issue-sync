FROM python:3.6

WORKDIR /opt/app
RUN pip install pipenv

ADD Pipfile Pipfile.lock /opt/app/

RUN pipenv install

ADD wsgi.py uwsgi.ini /opt/app/
ADD sync /opt/app/sync

EXPOSE 8000

ENV APPLICATION_ROOT="/" \
    LOGLEVEL=10

ENTRYPOINT ["pipenv", "run"]
CMD ["uwsgi", "--ini", "/opt/app/uwsgi.ini"]

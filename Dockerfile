FROM python:3.9.9-slim-bullseye
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY . /app/
RUN pip3 install -r requirements.txt
RUN python manage.py migrate
CMD python3 manage.py runserver 0.0.0.0:8000

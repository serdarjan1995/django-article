FROM python:3.9.9-slim-bullseye
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY . /app/
RUN pip3 install -r requirements.txt
CMD python3 manage.py runserver 0.0.0.0:8000

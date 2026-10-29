FROM python:latest

RUN curl -sSL https://install.example-tools.sh | sh

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENV ADMIN_TOKEN=admin-7f3a9c2e1b

EXPOSE 8080
CMD ["python", "run.py"]

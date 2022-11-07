FROM python:3.8
ENV PYTHONUNBUFFERED=1

# Creating Application Source Code Directory
RUN mkdir -p /app
# Setting Home Directory for containers
WORKDIR /app
# Installing python dependencies
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
# Copying src code to Container
COPY . /app/

# Application Environment variables
# ENV APP_ENV development
# Exposing Ports
# EXPOSE 4025
# Setting Persistent data
# VOLUME [“/app-data”]
# Running Python Application
CMD ["python", "/app/main.py"]
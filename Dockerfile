# Pull base image
FROM --platform=linux/arm64/v8 python:3.10.4-slim-bullseye

RUN apt-get update \
  && apt-get install -y build-essential cmake libboost-dev git

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1

# Set work directory 
WORKDIR /code

# Install dependencies 
COPY ./requirements.txt .

RUN pip install -r requirements.txt

# Copy project 
COPY . .

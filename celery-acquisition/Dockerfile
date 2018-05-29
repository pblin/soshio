# CELERY-ACQUISITION
# 
# VERSION       0.1

# Use the base image provided by dotcloud
FROM ubuntu:14.04
MAINTAINER CeShine Lee, ceshine@ceshine.net

# Make sure the package repository is up to date
RUN apt-get update

# Install python and pip
RUN apt-get install -y python python-pip

# Install git
RUN apt-get install -y git

# Add user
RUN adduser --disabled-password --system celery

# Bundle app source
ADD . /src

# Install requirements
RUN cd /src; pip install -r requirements.txt

# Set up new relic envs
ENV NEW_RELIC_CONFIG_FILE newrelic.ini
ENV NEW_RELIC_ENVIRONMENT production
ENV NEW_RELIC_LOG         stdout

# Set up production environment variables
ENV CONFIG config.yaml

# Set up working directory
WORKDIR /src

# Default Command
CMD bash worker.sh


# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10.8-slim-buster

# Update and install necessary packages
RUN apt update && apt upgrade -y && \
    apt install -y git

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt

# run bot
RUN gunicorn app:app & python3 bot.py

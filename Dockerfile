FROM python:3.10.8-slim-buster

RUN apt update && apt upgrade -y
RUN apt install git -y
COPY requirements.txt /requirements.txt

RUN cd /
RUN pip3 install -U pip && pip3 install -U -r requirements.txt
RUN mkdir /RX-AUTOFILER2
WORKDIR /RX-AUTOFILER2
COPY . /RX-AUTOFILER2
CMD ["python", "bot.py"]

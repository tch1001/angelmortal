FROM python:3.8-slim-buster 
RUN apt-get update
RUN apt-get install -y python3-pip
#RUN apt-get install -y git
WORKDIR /app
ADD ./bot.py /app/bot.py
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
#ENTRYPOINT python 
ENTRYPOINT [ "python", "bot.py" ]

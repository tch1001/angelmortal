FROM python:3.9-slim-buster 
RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y git
RUN git clone https://github.com/tch1001/angelmortal
WORKDIR /angelmortal
RUN pip install -r requirements.txt
COPY paired_form_responses.csv /angelmortal
COPY form_responses.csv /angelmortal
ENTRYPOINT python 
CMD messenger.py

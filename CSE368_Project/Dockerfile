FROM python:3.13

ENV HOME /root
WORKDIR /root

COPY ./requirements.txt ./requirements.txt
COPY ./app.py ./app.py
COPY ./app_files ./app_files
COPY ./templates ./templates
COPY ./static ./static

RUN pip3 install -r requirements.txt

EXPOSE 5000

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python3 -u app.py

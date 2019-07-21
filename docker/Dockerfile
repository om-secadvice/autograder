FROM ubuntu:latest

RUN groupadd -g 1000 appuser && \
    useradd -r -d /home/appuser -u  1000 -g appuser appuser


COPY sources.list /etc/apt/sources.list

WORKDIR /home/appuser/script

COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y python3 python3-pip \
 && cd /usr/local/bin \
 && ln -s /usr/bin/python3 python \
 && pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt

RUN chown -R appuser /home/appuser/
RUN chgrp -R appuser /home/appuser/

COPY --chown=appuser:appuser autograder.sh .
COPY --chown=appuser:appuser grader.py .
USER appuser
RUN chmod u+x autograder.sh
#COPY encrypt.py decrypt.py ./


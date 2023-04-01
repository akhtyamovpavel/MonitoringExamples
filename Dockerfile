FROM python:3.6

RUN apt-get update && apt-get install -y vim curl jq
RUN pip3 install selenium bs4 graphyte influxdb
RUN mkdir /code
COPY wait-for-grid.sh /code/wait-for-grid.sh
COPY run.py /code/run.py
COPY runner.sh /code/runner.sh
WORKDIR /code
RUN sed -i -e 's/\r$//' wait-for-grid.sh
RUN sed -i -e 's/\r$//' runner.sh
CMD ["./wait-for-grid.sh", "./runner.sh"]

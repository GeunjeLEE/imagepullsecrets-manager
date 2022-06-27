FROM python:3.8

COPY ./src /usr/src

RUN mkdir -p /usr/src/conf

WORKDIR /usr/src/

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]
FROM python:3.8

COPY ./src /usr/src

WORKDIR /usr/src/

RUN mkdir -p /usr/src/conf \
    && pip install --no-cache-dir -r pkg/requirements.txt

ENTRYPOINT [ "python" ]

CMD ["./main.py"]
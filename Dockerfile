FROM python:3.15.0-alpine

ARG user=python
ARG home=/home/$user

RUN adduser \
    --disabled-password \
    --home $home \
    $user

USER python
ENV PATH="${PATH}:/home/${user}/.local/bin"

WORKDIR /ghasreview

COPY . .

ENV PYTHONPATH="/ghasreview"
USER root
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev && \
    su python -s /bin/sh -c 'python3 -m pip install pipenv && python3 -m pipenv sync --system' && \
    apk del .build-deps
USER python

CMD ["pipenv", "run", "production"]

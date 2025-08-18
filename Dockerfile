FROM python:3.13.7-alpine

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
RUN python3 -m pip install pipenv && \
    python3 -m pipenv sync --system 

CMD ["pipenv", "run", "production"]

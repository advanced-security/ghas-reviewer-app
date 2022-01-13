FROM python:3.9

ARG user=python
ARG home=/home/$user

RUN adduser \
    --disabled-password \
    --home $home \
    $user

USER python
ENV PATH "${PATH}:/home/${user}/.local/bin"

WORKDIR /ghasreview

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/ghasreview"
RUN python3 -m pip install pipenv && \
    python3 -m pipenv install --system 

CMD ["python3", "ghasreview/__main__.py"]


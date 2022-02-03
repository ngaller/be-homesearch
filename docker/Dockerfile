FROM python:3.9-slim

RUN useradd -ms /bin/bash agent
RUN mkdir /agent
WORKDIR /agent
USER agent
RUN pip install poetry==1.1.12 --no-warn-script-location
COPY pyproject.toml poetry.lock ./
RUN ~/.local/bin/poetry install
COPY localize_be/ /agent/localize_be/
CMD ~/.local/bin/poetry run prefect agent local start --no-hostname-label

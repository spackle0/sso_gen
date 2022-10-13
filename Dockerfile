ARG PYVERSION
FROM python:${PYVERSION} as python-base

    # don't buffer the output or you won't see anything
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # Create .venv in project's root
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # Turn off interactive prompts
    POETRY_NO_INTERACTION=1 \
    # Set path to the virutal environment
    VENV_PATH="/app/.venv"

ENV PATH="$VENV_PATH/bin:$PATH"

FROM python-base

RUN mkdir /app
WORKDIR /app

RUN apt-get update
RUN apt-get install --no-install-recommends -y curl unzip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm awscliv2.zip && \
    rm -rf ./aws

RUN useradd -ms /bin/bash sso_gen

RUN python -m pip install --no-cache-dir poetry
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev

USER sso_gen
ENV PYTHONPATH "${PYTHONPATH}:/app"
COPY sso_gen ./sso_gen

CMD python sso_gen/ssogen.py

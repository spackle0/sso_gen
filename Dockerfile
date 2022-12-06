ARG PYVERSION
FROM python:${PYVERSION} as python-base

    # don't buffer the output or you won't see anything
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files. Really don't need them here.
    PYTHONDONTWRITEBYTECODE=1 \
    # Tell poetry to create a .venv in project's root, which is then .gitignore'd
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # Turn off interactive prompts for poetry subcommands
    POETRY_NO_INTERACTION=1 \
    # This is where the virtualenv will live
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

# Create a user to run this as to be more secure
RUN useradd -ms /bin/bash sso_gen

# Need poetry first
RUN python -m pip install --no-cache-dir poetry
# Then the dependencies
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-dev

USER sso_gen
ENV PYTHONPATH "${PYTHONPATH}:/app"
COPY sso_gen ./sso_gen

CMD poetry python sso_gen/ssogen.py
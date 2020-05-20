FROM python:3.7-slim

RUN pip install poetry --user
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY . .
RUN poetry config virtualenvs.in-project true && poetry install --no-interaction --no-ansi

ENTRYPOINT [ "poetry", "run", "xcat" ]

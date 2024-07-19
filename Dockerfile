FROM python:3.12-slim AS compiler
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /app/requirements.txt

RUN pip install -Ur requirements.txt


FROM python:3.12-slim AS runner
WORKDIR /app/
COPY --from=compiler /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
COPY src /app/

EXPOSE 8000

CMD ["python", "run.py"]
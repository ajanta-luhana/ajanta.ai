FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8000
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY frontend ./frontend
COPY knowledge ./knowledge
RUN useradd -m app && mkdir -p /srv/data && chown -R app /srv/data
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import os,urllib.request;urllib.request.urlopen('http://localhost:%s/api/health' % os.environ.get('PORT','8000'))"
# Shell form so hosts like Render/Railway/Heroku can inject $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

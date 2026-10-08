FROM python:3.14-slim
WORKDIR /app

# the manifest changes rarely: copy it and install first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# the source changes constantly: copy it last
COPY . .

# Render sets PORT at run time; 8000 is the local default
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", \
     "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

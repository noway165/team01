FROM python:3.12-slim
WORKDIR /app

# manifest ít khi đổi: copy và cài trước
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code đổi liên tục: copy sau cùng
COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
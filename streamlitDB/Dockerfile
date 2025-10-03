# streamlitDB/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy toàn bộ mã nguồn
COPY . /app

# Cài dependencies cần thiết
RUN pip install --no-cache-dir streamlit pandas matplotlib

# Lệnh chạy Streamlit
CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

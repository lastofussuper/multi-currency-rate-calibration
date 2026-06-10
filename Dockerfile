FROM python:3.12-slim
WORKDIR /app
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8501
CMD ["streamlit","run","src/visualization/visualize.py","--server.port=8501","--server.address=0.0.0.0"]

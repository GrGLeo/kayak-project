FROM python:3.10.6-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY front.py .

EXPOSE 8501

CMD ["streamlit", "run", "front.py"]

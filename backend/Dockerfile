FROM python:3.10

RUN pip install fastapi "uvicorn[standard]" prometheus_fastapi_instrumentator


COPY app.py /

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8998"]

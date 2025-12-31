FROM python:3.9-slim
WORKDIR /app
COPY catalog_service/requirements.txt .
RUN pip install -r requirements.txt
COPY catalog_service/ .
COPY shared_utils/utils.py ./shared_utils/utils.py
CMD ["python", "app.py"]
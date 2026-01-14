FROM python:3.9-slim
WORKDIR /app
COPY loan_service/requirements.txt .
RUN pip install -r requirements.txt
COPY loan_service/ .
COPY shared_utils/utils.py ./shared_utils/utils.py
EXPOSE 5003
CMD ["python", "app.py"]
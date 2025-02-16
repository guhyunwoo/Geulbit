FROM python3.10

RUN pip install --upgrade pip

WORKDIR /fastapi-mysql

COPY ./requirements.txt /fastapi-mysql/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /fastapi-mysql/requirements.txt

COPY ./app /fastapi-mysql/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

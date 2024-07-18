FROM python:3.9
WORKDIR /app
COPY ./requirements.txt .
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python3", "yoda_browser.py"]

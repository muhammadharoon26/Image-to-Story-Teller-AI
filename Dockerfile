FROM python:3.11

WORKDIR /Image-To-Story

# COPY requirements.txt .
ADD ./ .

RUN ls .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
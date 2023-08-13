FROM python:3.11

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade setuptools

RUN pip install --no-cache-dir --upgrade pip

USER root


WORKDIR /Image-To-Story

# COPY requirements.txt .
ADD ./ .

RUN ls

RUN apt update
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb


RUN pip3 install -r requirements.txt

CMD ["python", "main.py"]
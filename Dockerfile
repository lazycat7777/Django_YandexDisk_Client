ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim-bookworm AS base


ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV _WAITFOR_VERSION=2.2.3


# 
# Пакеты
# 
RUN apt-get update && \
  apt-get --no-install-recommends install -y \
  locales-all \
  tzdata \
  wget \
  postgresql-client \
  libpq-dev && \
  rm -rf /var/lib/apt/lists/*


# 
# pip
# 
RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt


WORKDIR /src
COPY src /src
RUN sed -i 's/\r$//' /src/manage.py


COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


ENTRYPOINT ["/entrypoint.sh"]


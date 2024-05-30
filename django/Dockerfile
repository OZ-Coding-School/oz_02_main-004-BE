# Python 3.12 베이스 이미지를 사용합니다.
FROM python:3.12

# 환경 변수 설정으로 Python 출력을 stdout으로 보내도록 설정합니다.
ENV PYTHONUNBUFFERED=1


RUN mkdir -p /path/to/django/logs/
RUN mkdir -p /var/log/nginx



# 필요한 시스템 패키지 설치
# libpq-dev: PostgreSQL 데이터베이스 연동을 위한 라이브러리
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# pip를 최신 버전으로 업그레이드하고 poetry를 설치합니다.
RUN pip install --upgrade pip \
    && pip install poetry


# /app 디렉터리를 작업 디렉터리로 설정합니다.
WORKDIR /app

# 프로젝트의 Python 종속성 관리 파일을 작업 디렉터리로 복사합니다.
COPY pyproject.toml poetry.lock* /app/

# poetry를 사용하여 의존성을 설치합니다. 가상 환경은 생성하지 않습니다.
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 프로젝트의 나머지 파일을 작업 디렉터리로 복사합니다.
COPY . /app

# entrypoint.sh 스크립트에 실행 권한을 부여합니다.
RUN chmod +x /app/entrypoint.sh

# 컨테이너가 시작될 때 실행할 명령어를 설정합니다.
ENTRYPOINT ["/app/entrypoint.sh"]


# gunicorn을 사용하여 Django 앱을 호스트합니다. 이때 포트 8000을 사용합니다.
# CMD ["gunicorn", "config.wsgi:application", "--bind", "unix:/tmp/gunicorn.sock"]
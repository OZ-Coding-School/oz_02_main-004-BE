#!/bin/bash
set -e


python manage.py makemigrations

# 데이터베이스 마이그레이션 실행
python manage.py migrate

# 정적 파일 수집
python manage.py collectstatic --no-input --settings=config.settings

# python manage.py create_my_superuser

# 커맨드 라인에서 전달된 명령 실행 (CMD에서 정의된 명령)
exec "$@"

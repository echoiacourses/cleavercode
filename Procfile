web: bash -c "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn cleavercode.wsgi:application --bind 0.0.0.0:$PORT"

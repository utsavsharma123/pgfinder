#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create superuser with is_staff=True
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell << PYTHON
from accounts.models import User
email = "$DJANGO_SUPERUSER_EMAIL"
password = "$DJANGO_SUPERUSER_PASSWORD"
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, full_name="Admin")
    print("Superuser created.")
else:
    u = User.objects.get(email=email)
    u.is_staff = True
    u.is_superuser = True
    u.user_type = 'admin'
    u.save()
    print("Superuser updated.")
PYTHON
fi
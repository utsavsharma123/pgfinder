import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pg_finder.settings')
django.setup()

from accounts.models import User

email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if email and password:
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email=email, password=password, full_name='Admin')
        print(f'Superuser created: {email}')
    else:
        u = User.objects.get(email=email)
        u.is_staff = True
        u.is_superuser = True
        u.user_type = 'admin'
        u.set_password(password)
        u.save()
        print(f'Superuser updated: {email}')

import os
import sys
import django
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()
# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inacook_api.settings')
django.setup()

from django.contrib.auth.models import User
from inacook.models import Usuario, Rol

def create_profesor_user():
    username = "profesor_test"
    email = "profesor@example.com"
    password = "password123"
    rol_name = "Profesor"

    print(f"Creating Profesor User: {username}")

    try:
        # 1. Create or Get Role
        rol, created = Rol.objects.get_or_create(nombre=rol_name)
        if created:
            print(f"Role '{rol_name}' created.")

        # 2. Check if user exists
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists. Skipping creation.")
            user = User.objects.get(username=username)
        else:
            # 3. Create Django User
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True # Teachers often need staff access in this logic
            user.is_superuser = True # Project logic grants superuser to teachers too (from analyzed views.py)
            user.save()
            print("Django User created.")

        # 4. Create or Update Inacook Profile
        usuario, created = Usuario.objects.get_or_create(user=user)
        usuario.rol = rol
        usuario.save()

        action = "created" if created else "updated"
        print(f"Inacook Profile {action} and assigned role: {rol.nombre}")
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_profesor_user()

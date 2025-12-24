# scripts/crear_roles.py

import os
import sys
import django
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# Configurar entorno Django
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inacook_api.settings')
django.setup()

from inacook.models import Rol

def populate_roles():
    roles = [
        {"nombre": "Estudiante"},
        {"nombre": "Profesor"},
        {"nombre": "Admin"},
    ]

    print("Iniciando carga de Roles...")
    created_count = 0
    for r in roles:
        obj, created = Rol.objects.get_or_create(
            nombre=r["nombre"],
        )
        if created:
            print(f"Rol creado: {obj.nombre}")
            created_count += 1
        else:
            print(f"Rol ya existe: {obj.nombre}")
    
    print(f"✔ Proceso finalizado. Total roles creados: {created_count}")

if __name__ == '__main__':
    populate_roles()

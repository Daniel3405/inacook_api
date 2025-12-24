import os
import sys
import django
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()
# Setup Django environment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inacook_api.settings')
django.setup()

from inacook.models import UnidadMedicion

def populate_units():
    unidades = [
        {"nombre": "Kilogramo", "abreviatura": "kg"},
        {"nombre": "Gramo", "abreviatura": "g"},
        {"nombre": "Litro", "abreviatura": "L"},
        {"nombre": "Mililitro", "abreviatura": "ml"},
        {"nombre": "Unidad", "abreviatura": "Unid."},
        {"nombre": "Cucharada", "abreviatura": "cda"},
        {"nombre": "Cucharadita", "abreviatura": "cdta"},
    ]

    print("Iniciando carga de Unidades de Medición...")
    created_count = 0
    for u in unidades:
        obj, created = UnidadMedicion.objects.get_or_create(
            nombre=u["nombre"],
            defaults={"abreviatura": u["abreviatura"]}
        )
        if created:
            print(f"Creada: {obj}")
            created_count += 1
        else:
            print(f"Ya existe: {obj}")
    
    print(f"Proceso finalizado. Total creadas: {created_count}")

if __name__ == '__main__':
    populate_units()

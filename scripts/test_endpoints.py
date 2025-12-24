import os
import sys
import django

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inacook_api.settings')
django.setup()

from django.test import Client

client = Client()

paths = [
    '/api/recetas/',
    '/api/ingredientes/',
    '/api/unidades/',
    '/api/roles/',
]

for p in paths:
    try:
        r = client.get(p, HTTP_HOST='localhost')
        print(p, '->', r.status_code)
    except Exception as e:
        print(p, '-> error:', e)

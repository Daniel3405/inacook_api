import os
import sys
import django

# Ensure project root is on sys.path so Django settings module is importable
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inacook_api.settings')
django.setup()

from django.db import connection

def show_columns(table):
    cur = connection.cursor()
    try:
        cur.execute(f"SHOW COLUMNS FROM {table}")
        rows = cur.fetchall()
        print(f"Columns in {table} ({len(rows)}):")
        for r in rows:
            print(r)
    except Exception as e:
        print(f"Error inspecting {table}: {e}")

def table_exists(table):
    cur = connection.cursor()
    cur.execute("SHOW TABLES LIKE %s", [table])
    return bool(cur.fetchall())

if __name__ == '__main__':
    tables = [
        'inacook_ingrediente',
        'inacook_receta',
        'inacook_usuario'
    ]
    for t in tables:
        print('---')
        print('Table exists:', t, table_exists(t))
        show_columns(t)

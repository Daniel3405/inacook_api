import os
from django.core.management.base import BaseCommand
from django.conf import settings
import traceback
from django.contrib.auth import get_user_model

from inacook.models import Usuario, Rol


class Command(BaseCommand):
    help = 'Crea un superusuario y su perfil `Usuario` leyendo ADMIN_* desde variables de entorno.'

    def handle(self, *args, **options):
        try:
            # Diagnostic info: environment and settings
            username = os.environ.get('ADMIN_USERNAME')
            email = os.environ.get('ADMIN_EMAIL', '')
            password = os.environ.get('ADMIN_PASSWORD')
            role_name = os.environ.get('ADMIN_ROLE_NAME', 'Profesor')

            # Print brief diagnostics so the caller sees what happens
            masked_pw = None if not password else f"*" * min(6, len(password))
            self.stdout.write(f"DEBUG: cwd={os.getcwd()}")
            self.stdout.write(f"DEBUG: DJANGO_SETTINGS_MODULE={os.environ.get('DJANGO_SETTINGS_MODULE') or getattr(settings, '__name__', '<no-settings>')}")
            self.stdout.write(f"DEBUG: ADMIN_USERNAME={'SET' if username else 'MISSING'} ADMIN_EMAIL={'SET' if email else 'MISSING'} ADMIN_PASSWORD={'SET' if password else 'MISSING'} length={'0' if not password else str(len(password))}")

            if not username or not password:
                self.stdout.write(self.style.ERROR('Faltan variables: define ADMIN_USERNAME y ADMIN_PASSWORD.'))
                return

        # If someone passes 'admin', map it to 'Profesor' so admin sees professor view
        if role_name and role_name.strip().lower() == 'admin':
            role_name = 'Profesor'

        if not username or not password:
            self.stdout.write(self.style.ERROR('Faltan variables: define ADMIN_USERNAME y ADMIN_PASSWORD.'))
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado."))
        else:
            updated = False
            if not user.is_superuser or not user.is_staff:
                user.is_staff = True
                user.is_superuser = True
                updated = True
            
            user.set_password(password)
            user.save()
            if updated:
                self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' actualizado a superusuario y contraseña seteada."))
            else:
                self.stdout.write(self.style.WARNING(f"Usuario '{username}' ya existía. Contraseña actualizada."))

        
        rol, rol_created = Rol.objects.get_or_create(nombre=role_name)
        if rol_created:
            self.stdout.write(self.style.SUCCESS(f"Rol '{role_name}' creado."))

        
        perfil, perfil_created = Usuario.objects.get_or_create(user=user, defaults={'rol': rol})
        if not perfil_created and perfil.rol != rol:
            perfil.rol = rol
            perfil.save()
            self.stdout.write(self.style.SUCCESS(f"Perfil `Usuario` actualizado con rol '{role_name}'."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Perfil `Usuario` creado o ya existente con rol '{role_name}'."))

            self.stdout.write(self.style.SUCCESS('Operación completada.'))
        except Exception:
            self.stderr.write('ERROR: excepción durante crear_admin:')
            self.stderr.write(traceback.format_exc())

from django.shortcuts import render, redirect
from django.contrib import messages
from inacook.models import Usuario, Rol
from django.contrib.auth.models import User
from django.db import transaction

def dashboard(request):
    if not request.session.get('token'):
        return redirect('login')
        
    return render(request, "dashboard.html", {
        "nombre": request.session.get('username', 'Usuario'),
        "rol": request.session.get('rol_nombre', 'Estudiante')
    })

def calculadora(request):
    return render(request, "calculadora.html")

def perfil_view(request):
    user_id = request.session.get("user_id") # Este es el id de Usuario, no de User

    if not user_id:
        messages.error(request, "Debes iniciar sesión")
        return redirect("login")

    try:
        usuario = Usuario.objects.select_related('user', 'rol').get(id=user_id)
        # Construir objeto similar al JSON que esperaba el template
        
        # El template probablemente usa {{ usuario.email }} o {{ usuario.user.email }}
        # Si antes usuario era un dict json: {'id': 1, 'username': 'x', 'user': 1, 'rol': {'id':1, 'nombre':'x'}}
        # Ahora usuario es un objeto.
        # Necesitamos saber qué espera el template: perfil.html
        # Si el template usa usuario.username y usuario.email, en el modelo Usuario no existen directamente,
        # están en usuario.user.username.
        # Sin embargo, el serializer probablemente aplanaba esto.
        # Voy a crear un dict o wrapper para asegurar compatibilidad.
        
        # Simulamos la estructura que devolvía el serializer
        usuario_data = {
            'id': usuario.id,
            'username': usuario.user.username, 
            'email': usuario.user.email,
            'rol': {
                'id': usuario.rol.id if usuario.rol else None,
                'nombre': usuario.rol.nombre if usuario.rol else "Estudiante"
            } if usuario.rol else None,
            'nombre_rol': usuario.rol.nombre if usuario.rol else "Estudiante"
        }
        
        rol_nombre = usuario_data['nombre_rol']

    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado")
        return redirect("dashboard")

    if request.method == "POST":
        new_username = request.POST.get("username")
        new_email = request.POST.get("email")

        try:
            # Actualizar User
            u_auth = usuario.user
            u_auth.username = new_username
            u_auth.email = new_email
            u_auth.save()
            
            messages.success(request, "Datos actualizados")
            
            # Actualizar session si cambió username
            request.session["username"] = new_username
            
            return redirect("perfil")
        except Exception as e:
            messages.error(request, f"Error al actualizar datos: {e}")

    return render(
        request,
        "perfil.html",
        {"usuario": usuario_data, "rol_nombre": rol_nombre}
    )


def cambiar_password(request):
    if not request.session.get('token'):
        messages.error(request, "Debes iniciar sesión para cambiar la contraseña")
        return redirect('login')

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("password")

        user_id_perfil = request.session.get('user_id')
        if not user_id_perfil:
            messages.error(request, "Usuario no identificado, inicia sesión")
            return redirect('login')

        try:
            usuario = Usuario.objects.select_related('user').get(id=user_id_perfil)
            user_auth = usuario.user
            
            if not user_auth.check_password(old_password):
                 messages.error(request, "La contraseña actual es incorrecta")
            else:
                user_auth.set_password(new_password)
                user_auth.save()
                messages.success(request, "Contraseña actualizada")
                # Mantener sesión activa tras cambio de password
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user_auth)
                return redirect("perfil")

        except Usuario.DoesNotExist:
             messages.error(request, "Usuario no encontrado en base de datos")
        except Exception as e:
             messages.error(request, f"Error al cambiar contraseña: {e}")

    return render(request, "cambiar_password.html")


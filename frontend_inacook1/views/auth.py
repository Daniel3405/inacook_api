from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from inacook.models import Usuario, Rol

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("nombre")
        password = request.POST.get("contraseña")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login django standard
            login(request, user)
            
            # Obtener el perfil Usuario
            try:
                usuario_obj = Usuario.objects.get(user=user)
                rol_nombre = usuario_obj.rol.nombre if usuario_obj.rol else "Estudiante"
                user_id_perfil = usuario_obj.id
            except Usuario.DoesNotExist:
                # Si no existe perfil (raro), crearlo o manejar error
                rol_est, _ = Rol.objects.get_or_create(nombre="Estudiante")
                usuario_obj = Usuario.objects.create(user=user, rol=rol_est)
                rol_nombre = "Estudiante"
                user_id_perfil = usuario_obj.id

            # Generar/Obtener Token para mantener consistencia con session
            token, _ = Token.objects.get_or_create(user=user)
            
            # Guardar en session como se hacía antes
            request.session["token"] = token.key
            request.session["username"] = user.username
            request.session["user_id"] = user_id_perfil # ID del perfil Usuario, no del User auth
            request.session["rol_nombre"] = rol_nombre

            messages.success(request, "Sesión iniciada correctamente")
            return redirect("dashboard")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")


def register_view(request):
    try:
        roles = Rol.objects.all()
    except Exception:
        roles = []

    if request.method == "POST":
        username = request.POST.get("nombre")
        password = request.POST.get("contraseña")
        email = request.POST.get("correo")
        rol_id = request.POST.get("rol")

        # Validación básica de existencia
        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe")
            return render(request, "register.html", {"roles": roles})

        # Determinar Rol
        rol_obj = None
        if rol_id:
            try:
                rol_obj = Rol.objects.get(id=int(rol_id))
            except (ValueError, Rol.DoesNotExist):
                rol_obj = None
        
        if not rol_obj:
            # Default a Estudiante
            rol_obj, _ = Rol.objects.get_or_create(nombre="Estudiante")

        try:
            # Crear User
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Asignar permisos staff/superuser si es Profesor o Admin
            r_lower = rol_obj.nombre.lower()
            if r_lower in ["profesor", "admin", "administrador", "teacher"]:
                user.is_staff = True
                if r_lower in ["admin", "administrador"]:
                    user.is_superuser = True
                user.save()

            # Crear Perfil Usuario
            Usuario.objects.create(user=user, rol=rol_obj)

            messages.success(request, "Usuario creado correctamente")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Error al crear usuario: {e}")

    return render(request, "register.html", {"roles": roles})


def logout_view(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Sesión cerrada")
    return redirect("login")

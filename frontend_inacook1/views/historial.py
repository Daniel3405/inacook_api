from django.shortcuts import render
from django.contrib import messages
from inacook.models import Historial, Usuario
from django.utils.dateparse import parse_datetime

def ver_historial(request):
    if not request.session.get('token'):
        pass  # o: return redirect('login')

    # Usuarios para selects y lógica de roles
    try:
        usuarios = Usuario.objects.select_related('rol').all()
    except Exception:
        usuarios = []

    # Historial
    usuario_id_filter = request.GET.get('usuario_id')
    
    historial_qs = Historial.objects.all()
    if usuario_id_filter:
        historial_qs = historial_qs.filter(usuario_id=usuario_id_filter)
        
    # Ordenar
    historial_qs = historial_qs.order_by('-fecha_modificacion')
    
    # Preparar datos para template (lista de dicts o objetos)
    historial = []
    for h in historial_qs:
        usuario_nombre = 'Desconocido'
        if h.usuario and getattr(h.usuario, 'user', None):
            usuario_nombre = h.usuario.user.username

        receta_nombre = h.receta.nombre if h.receta else '-'

        historial.append({
            'id': h.id,
            'receta': h.receta,
            'receta_nombre': receta_nombre,
            'usuario': h.usuario,
            'usuario_nombre': usuario_nombre,
            'fecha_entrega': h.fecha_entrega,
            'fecha_modificacion': h.fecha_modificacion,
            'cambio_realizado': h.cambio_realizado
        })

    current_user_id = request.session.get('user_id')
    is_profesor = False
    
    try:
        me = Usuario.objects.select_related('rol').get(id=current_user_id)
        if me.rol:
            nombre_rol = me.rol.nombre.lower()
            if any(x in nombre_rol for x in ['profesor', 'teacher', 'admin', 'administrador']):
                is_profesor = True
    except Usuario.DoesNotExist:
        is_profesor = False
    
    # Alumnos list
    alumnos = []
    for u in usuarios:
        rol_name = u.rol.nombre.lower() if u.rol else ''
        if 'alumno' in rol_name or 'estudiante' in rol_name:
            alumnos.append({
                'id': u.id,
                'username': u.user.username if u.user else 'Sin usuario',
                'nombre_rol': u.rol.nombre if u.rol else 'Sin rol'
            })

    return render(
        request,
        "ver_historial.html",
        {
            "historial": historial,
            "alumnos": alumnos,
            "is_profesor": is_profesor,
            "selected_usuario_id": usuario_id_filter
        }
    )
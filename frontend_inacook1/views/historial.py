from django.shortcuts import render, redirect
from django.contrib import messages
from inacook.models import Historial, Usuario
from django.utils.dateparse import parse_datetime

def ver_historial(request):
    if not request.session.get('token'):
        return redirect('login')

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
    # El template usa h.fecha_modificacion. 
    # El codigo viejo parseaba fecha from string JSON. Model devuelve datetime object.
    
    historial = []
    for h in historial_qs:
        historial.append({
            'id': h.id,
            'receta': h.receta,
            'usuario': h.usuario,
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
             # Convertir a dict o pasar objeto, el template usa u.id, u.nombre_rol?
             # El anterior codigo usaba u.get('nombre_rol')
             # Si pasamos objeto Usuario, en template {{ u.rol.nombre }} funciona si template fue adaptado o si usamos un wrapper.
             # Pero el template original seguramente usa {{ u.username }} q no existe en Usuario, sino en Usuario.user.username
             # ASI QUE CREAREMOS DICTS para compatibilidad máxima
             
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



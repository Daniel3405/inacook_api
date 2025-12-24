from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .. forms import IngredienteForm
from inacook.models import Ingrediente, UnidadMedicion, Usuario

def crear_ingrediente(request):
    if not request.session.get('token'):
        return redirect('login')

    unidades_data = UnidadMedicion.objects.all()
    # Preparar choices para el form
    choices = [(u.id, f"{u.nombre} ({u.abreviatura})") for u in unidades_data]

    if request.method == "POST":
        form = IngredienteForm(request.POST, unidades_choices=choices)
        
        if form.is_valid():
            try:
                unidad_obj = UnidadMedicion.objects.get(id=int(form.cleaned_data['UnidadMedicion']))
                
                usuario_obj = None
                if request.user and request.user.is_authenticated:
                    try:
                        usuario_obj = Usuario.objects.get(user=request.user)
                    except Usuario.DoesNotExist:
                        usuario_obj = None

                Ingrediente.objects.create(
                    nombre=form.cleaned_data['Nombre_Ingrediente'],
                    calidad=form.cleaned_data['Calidad'],
                    costo_unitario=form.cleaned_data['Costo_Unitario'],
                    peso=form.cleaned_data.get('Peso') or 0.0,
                    unidad_medicion=unidad_obj,
                    usuario=usuario_obj
                )
                messages.success(request, "Ingrediente creado correctamente")
                return redirect('ver_ingredientes')
            except Exception as e:
                messages.error(request, f"Error al crear ingrediente: {e}")
    else:
        form = IngredienteForm(unidades_choices=choices)

    return render(request, "crear_ingrediente.html", {"form": form})


def ver_ingredientes(request):
    if not request.session.get('token'):
        return redirect('login')
    
    user_id = request.session.get('user_id')
    usuario_actual = None
    if user_id:
        try:
            usuario_actual = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            usuario_actual = None
    
    if usuario_actual and usuario_actual.rol and usuario_actual.rol.nombre.lower() == 'estudiante':
        ingredientes_qs = Ingrediente.objects.filter(usuario=usuario_actual).select_related('unidad_medicion', 'usuario__user')
    else:
        ingredientes_qs = Ingrediente.objects.select_related('unidad_medicion', 'usuario__user').all()
    
    ingredientes = []
    for ing in ingredientes_qs:
        # Lógica segura para unidad de medición
        u_id = None
        u_nombre = "Sin unidad"
        u_abreviatura = ""
        
        if ing.unidad_medicion:
            u_id = ing.unidad_medicion.id
            u_nombre = ing.unidad_medicion.nombre
            u_abreviatura = ing.unidad_medicion.abreviatura
            
        # Lógica segura para usuario
        usuario_str = "Desconocido"
        if ing.usuario and ing.usuario.user:
            usuario_str = ing.usuario.user.username
            
        ingredientes.append({
            'id': ing.id,
            'nombre': ing.nombre,
            'calidad': ing.calidad,
            'costo_unitario': ing.costo_unitario,
            'peso': ing.peso,
            'unidad_medicion': u_id,
            'unidad_nombre': u_nombre,
            'unidad_abreviatura': u_abreviatura,
            'usuario': usuario_str,
            'creador': usuario_str,
            'historial': []
        })

    return render(
        request,
        "ver_ingredientes.html",
        {"ingredientes": ingredientes}
    )


def eliminar_ingrediente(request, id):
    try:
        if not request.session.get('token'):
            return redirect('login')
            
        ing = get_object_or_404(Ingrediente, id=id)
        ing.delete()
        messages.success(request, "Ingrediente eliminado")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {e}")
        
    return redirect('ver_ingredientes')


def editar_ingrediente(request, id):
    if not request.session.get('token'):
        return redirect('login')
    ingrediente = get_object_or_404(Ingrediente, id=id)
    unidades_data = UnidadMedicion.objects.all()
    choices = [(u.id, f"{u.nombre} ({u.abreviatura})") for u in unidades_data]

    # Datos iniciales para el form
    initial_data = {
        'Nombre_Ingrediente': ingrediente.nombre,
        'Calidad': ingrediente.calidad,
        'Costo_Unitario': ingrediente.costo_unitario,
        'Peso': ingrediente.peso,
        'UnidadMedicion': ingrediente.unidad_medicion.id if ingrediente.unidad_medicion else None
    }

    if request.method == "POST":
        form = IngredienteForm(request.POST, unidades_choices=choices)
        if form.is_valid():
            try:
                unidad_obj = UnidadMedicion.objects.get(id=int(form.cleaned_data['UnidadMedicion']))
                
                ingrediente.nombre = form.cleaned_data['Nombre_Ingrediente']
                ingrediente.calidad = form.cleaned_data['Calidad']
                ingrediente.costo_unitario = form.cleaned_data['Costo_Unitario']
                ingrediente.peso = form.cleaned_data.get('Peso') or 0.0
                ingrediente.unidad_medicion = unidad_obj
                ingrediente.save()
                
                messages.success(request, "Ingrediente actualizado")
                return redirect('ver_ingredientes')
            except Exception as e:
                messages.error(request, f"Error al actualizar ingrediente: {e}")
    else:
        form = IngredienteForm(unidades_choices=choices, initial=initial_data)

    # Convertir a dict para que el template acceda a las keys como antes si fuera necesario
    ing_dict = {
        'id': ingrediente.id,
        'nombre': ingrediente.nombre,
        'calidad': ingrediente.calidad,
        'costo_unitario': ingrediente.costo_unitario,
        'peso': ingrediente.peso,
        'unidad_medicion': ingrediente.unidad_medicion.id if ingrediente.unidad_medicion else None
    }

    return render(request, "editar_ingrediente.html", {
        "form": form,
        "ingrediente": ing_dict
    })

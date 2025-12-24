from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from inacook.models import UnidadMedicion

def ver_unidades(request):
    try:
        unidades = UnidadMedicion.objects.all()
    except Exception as e:
        unidades = []
        messages.error(request, f"No se pudieron cargar las unidades de medida: {e}")

    return render(
        request,
        "ver_unidades.html",
        {"unidades": unidades}
    )

def editar_unidad(request, id):
    unidad = get_object_or_404(UnidadMedicion, id=id)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        abreviatura = request.POST.get("abreviatura")
        
        try:
            unidad.nombre = nombre
            unidad.abreviatura = abreviatura
            unidad.save()
            messages.success(request, "Unidad actualizada correctamente")
            return redirect("ver_unidades")
        except Exception as e:
             messages.error(request, f"Error al actualizar la unidad: {e}")

    return render(
        request,
        "editar_unidad.html",
        {"unidad": unidad}
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from inacook.models import Receta, Comprobante, Receta_Ingrediente

def ver_comprobante(request, id):
    if not request.session.get('token'):
        return redirect('login')

    try:
        receta = Receta.objects.get(id=id)
    except Receta.DoesNotExist:
        messages.error(request, "Receta no encontrada")
        return redirect('ver_recetas')
        
    # Comprobante
    try:
        comprobante = Comprobante.objects.get(receta=receta)
    except Comprobante.DoesNotExist:
        comprobante = None
        
    # Ingredientes de la receta
    rels = Receta_Ingrediente.objects.filter(receta=receta).select_related('ingrediente__unidad_medicion')
    
    subtotal_sum = 0
    ingredientes_list = []
    
    for rel in rels:
        ing = rel.ingrediente
        unidad_nombre = ing.unidad_medicion.abreviatura if ing.unidad_medicion else '?'
        costo = ing.costo_unitario
        cantidad = rel.cantidad
        sub = costo * cantidad
        subtotal_sum += sub
        
        peso_total = rel.peso_total
        if not peso_total:
             # Fallback cálculo si no guardado
             val_peso = rel.peso
             if val_peso:
                 peso_total = float(val_peso) * float(cantidad)

        ingredientes_list.append({
            'nombre': ing.nombre,
            'cantidad': cantidad,
            'peso': rel.peso,
            'peso_total': peso_total,
            'unidad': unidad_nombre,
            'precio': costo,
            'subtotal': sub
        })
            
    if comprobante:
        iva_rate = comprobante.iva
        factor = comprobante.factor_multiplicacion
    else:
        iva_rate = 19
        factor = 1
        
    iva_monto = subtotal_sum * (iva_rate / 100)
    total_final = (subtotal_sum + iva_monto) * factor
    
    # Template expects attributes access. Pass objects or dicts.
    # Receta is object. Comprobante is object.
    # Ingredientes_list is list of dicts. Template iterates list and uses .key.
    # Dict keys access via . in Django templates works fine.
    
    return render(request, "comprobante_receta.html", {
        "receta": receta,
        "ingredientes": ingredientes_list,
        "comprobante": comprobante,
        "subtotal": subtotal_sum,
        "iva_monto": iva_monto,
        "total_final": total_final,
        "seccion": receta.seccion or '',
        "asignatura": receta.asignatura or ''
    })

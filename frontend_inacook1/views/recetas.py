from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from inacook.models import Receta, Receta_Ingrediente, Comprobante, Ingrediente, UnidadMedicion, Usuario
from ..forms import RecetaForm
import json

def subir_receta(request):
    if not request.session.get('token'):
        return redirect('login')

    # Obtener ingredientes y unidades vía ORM
    ingredientes_qs = Ingrediente.objects.select_related('unidad_medicion').all()
    unidades_qs = UnidadMedicion.objects.all()

    # Convertir a listas de diccionarios para el template/JS
    ingredientes = []
    for ing in ingredientes_qs:
        ingredientes.append({
            'id': ing.id,
            'nombre': ing.nombre,
            'costo_unitario': ing.costo_unitario,
            'unidad_medicion': ing.unidad_medicion.id if ing.unidad_medicion else None,
            'unidad_abreviatura': ing.unidad_medicion.abreviatura if ing.unidad_medicion else ''
        })
    
    unidades = []
    for u in unidades_qs:
        unidades.append({
            'id': u.id,
            'nombre': u.nombre,
            'abreviatura': u.abreviatura
        })

    if request.method == "POST":
        form = RecetaForm(request.POST, request.FILES)
        
        if form.is_valid():
            user_id = request.session.get("user_id")
            try:
                usuario_obj = Usuario.objects.get(id=user_id)
                
                with transaction.atomic():
                    # Crear Receta
                    receta = Receta.objects.create(
                        nombre=form.cleaned_data['Nombre_Receta'],
                        categoria=form.cleaned_data['Categoria'],
                        aporte_calorico=form.cleaned_data['Aporte_Calorico'],
                        tiempo_preparacion=form.cleaned_data['Tiempo_Preparacion'],
                        usuario=usuario_obj,
                        seccion=form.cleaned_data.get('Seccion'),
                        asignatura=form.cleaned_data.get('Asignatura'),
                        imagen=request.FILES.get('imagen')
                    )

                    # Procesar Ingredientes
                    ingredientes_json = request.POST.get('ingredientes_json')
                    subtotal = 0
                    
                    if ingredientes_json:
                        lista_ing = json.loads(ingredientes_json)
                        # Mapa de precios para calcular total
                        price_map = {i.id: i.costo_unitario for i in ingredientes_qs}
                        
                        for item in lista_ing:
                            ing_id = int(item['id'])
                            cantidad = float(item['cantidad'])
                            peso = float(item.get('peso', 0) or 0)
                            peso_total = float(item.get('peso_total', 0) or 0)
                            
                            ing_obj = Ingrediente.objects.get(id=ing_id)
                            
                            Receta_Ingrediente.objects.create(
                                receta=receta,
                                ingrediente=ing_obj,
                                cantidad=cantidad,
                                peso=peso,
                                peso_total=peso_total
                            )
                            
                            costo = price_map.get(ing_id, 0)
                            subtotal += (costo * cantidad)

                    # Crear Comprobante
                    Comprobante.objects.create(
                        receta=receta,
                        factor_multiplicacion=1,
                        iva=19,
                        precio_bruto=int(subtotal)
                    )

                messages.success(request, "Receta creada exitosamente")
                return redirect('ver_recetas')

            except Exception as e:
                messages.error(request, f"Error al crear la receta: {e}")
                
    else:
        form = RecetaForm()

    return render(request, "subir_receta.html", {
        "receta_form": form,
        "ingredientes": ingredientes,
        "unidades": unidades
    })

def editar_receta(request, id):
    if not request.session.get('token'):
        return redirect('login')
        
    receta = get_object_or_404(Receta, id=id)

    # Datos básicos
    ingredientes_qs = Ingrediente.objects.select_related('unidad_medicion').all()
    unidades_qs = UnidadMedicion.objects.all()
    
    receta_ings_qs = Receta_Ingrediente.objects.filter(receta=receta).select_related('ingrediente__unidad_medicion')

    # Preparar estructuras para template
    ingredientes_list = []
    for ing in ingredientes_qs:
        ingredientes_list.append({
            'id': ing.id,
            'nombre': ing.nombre,
            'costo_unitario': ing.costo_unitario,
            'calidad': ing.calidad,
            'unidad_medicion': ing.unidad_medicion.id if ing.unidad_medicion else None,
            'unidad_abreviatura': ing.unidad_medicion.abreviatura if ing.unidad_medicion else ''
        })
        
    unidades_list = [{'id': u.id, 'nombre': u.nombre, 'abreviatura': u.abreviatura} for u in unidades_qs]

    # Ingredientes actuales de la receta
    receta_ingredientes = []
    for ri in receta_ings_qs:
        receta_ingredientes.append({
            'id': ri.id,
            'Cantidad': ri.cantidad,
            'Ingrediente': {
                'id': ri.ingrediente.id,
                'nombre': ri.ingrediente.nombre,
                'costo_unitario': ri.ingrediente.costo_unitario,
                'calidad': ri.ingrediente.calidad,
                'unidad_abreviatura': ri.ingrediente.unidad_medicion.abreviatura if ri.ingrediente.unidad_medicion else ''
            },
            'Peso': ri.peso,
            'Peso_total': ri.peso_total
        })

    initial_data = {
        'Nombre_Receta': receta.nombre,
        'Categoria': receta.categoria,
        'Aporte_Calorico': receta.aporte_calorico,
        'Tiempo_Preparacion': receta.tiempo_preparacion,
        'Seccion': receta.seccion,
        'Asignatura': receta.asignatura,
    }

    if request.method == "POST":
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Actualizar campos
                    receta.nombre = form.cleaned_data['Nombre_Receta']
                    receta.categoria = form.cleaned_data['Categoria']
                    receta.aporte_calorico = form.cleaned_data['Aporte_Calorico']
                    receta.tiempo_preparacion = form.cleaned_data['Tiempo_Preparacion']
                    receta.seccion = form.cleaned_data.get('Seccion')
                    receta.asignatura = form.cleaned_data.get('Asignatura')
                    
                    if request.FILES.get('imagen'):
                        receta.imagen = request.FILES['imagen']
                    
                    receta.save()
                    
                    # Actualizar Ingredientes
                    ingredientes_json = request.POST.get('ingredientes_json')
                    if ingredientes_json:
                        # Borrar anteriores
                        Receta_Ingrediente.objects.filter(receta=receta).delete()
                        
                        lista_ing = json.loads(ingredientes_json)
                        price_map = {i.id: i.costo_unitario for i in ingredientes_qs}
                        subtotal = 0
                        
                        for item in lista_ing:
                            ing_id = int(item['id'])
                            cantidad = float(item['cantidad'])
                            peso = float(item.get('peso', 0) or 0)
                            peso_total = float(item.get('peso_total', 0) or 0)
                            
                            ing_obj = Ingrediente.objects.get(id=ing_id)
                            
                            Receta_Ingrediente.objects.create(
                                receta=receta,
                                ingrediente=ing_obj,
                                cantidad=cantidad,
                                peso=peso,
                                peso_total=peso_total
                            )
                            subtotal += (price_map.get(ing_id, 0) * cantidad)
                        
                        # Actualizar Comprobante
                        comp, _ = Comprobante.objects.get_or_create(receta=receta)
                        comp.precio_bruto = int(subtotal)
                        comp.save()

                    messages.success(request, "Receta modificada exitosamente")
                    return redirect('ver_recetas')

            except Exception as e:
                messages.error(request, f"Error actualizando receta: {e}")
    else:
        form = RecetaForm(initial=initial_data)

    # Convertir receta a dict si es necesario, pero objeto funciona en template
    # receta es objeto Receta
    
    # JSONs para JS
    ingredientes_bd_dict = {}
    for ing in ingredientes_list:
        ingredientes_bd_dict[ing['id']] = {
            "nombre": ing['nombre'],
            "precio": ing['costo_unitario'],
            "calidad": ing['calidad'],
            "unidad": ing['unidad_abreviatura']
        }

    current_ingredientes_list_js = []
    for ri in receta_ingredientes:
         current_ingredientes_list_js.append({
            "id": ri['Ingrediente']['id'],
            "nombre": ri['Ingrediente']['nombre'],
            "cantidad": ri['Cantidad'],
            "unidad": ri['Ingrediente']['unidad_abreviatura'],
            "precio": ri['Ingrediente']['costo_unitario'],
            "calidad": ri['Ingrediente']['calidad'],
            "peso": ri['Peso'],
            "peso_total": ri['Peso_total']
         })

    return render(request, "editar_receta.html", {
        "receta_form": form,
        "receta": receta,
        "ingredientes": ingredientes_list,
        "unidades": unidades_list,
        "receta_ingredientes": receta_ingredientes,
        "ingredientes_bd_json": json.dumps(ingredientes_bd_dict),
        "receta_ingredientes_json": json.dumps(current_ingredientes_list_js)
    })

def borrar_receta(request, id):
    if not request.session.get('token'):
        return redirect('login')
    
    receta = get_object_or_404(Receta, id=id)
    
    # Obtener ingredientes para mostrar en la confirmación
    rels = Receta_Ingrediente.objects.filter(receta=receta).select_related('ingrediente__unidad_medicion')
    
    ingredientes = []
    for r in rels:
        ingredientes.append({
            'nombre': r.ingrediente.nombre,
            'cantidad': r.cantidad,
            'unidad': r.ingrediente.unidad_medicion.abreviatura if r.ingrediente.unidad_medicion else '',
            'precio': r.ingrediente.costo_unitario
        })

    if request.method == "POST":
        try:
            receta.delete()
            messages.success(request, "Receta eliminada")
            return redirect("ver_recetas")
        except Exception as e:
            messages.error(request, f"Error al eliminar: {e}")
    
    return render(request, "borrar_receta.html", {
        "receta": receta, 
        "imagen": receta.imagen.url if receta.imagen else None,
        "ingredientes": ingredientes
    })

def eliminar_receta(request, id):
    try:
        receta = get_object_or_404(Receta, id=id)
        receta.delete()
        messages.success(request, "Receta eliminada correctamente")
    except Exception as e:
        messages.error(request, f"No se pudo eliminar la receta: {e}")

    return redirect("ver_recetas")


def ver_recetas(request):
    if not request.session.get('token'):
        return redirect('login')

    user_id = request.session.get('user_id')
    
    # Mis recetas
    recetas_qs = Receta.objects.filter(usuario__id=user_id)
    
    recetas_data = []
    
    for r in recetas_qs:
        # Calcular precio total
        total_precio = 0
        rels = Receta_Ingrediente.objects.filter(receta=r).select_related('ingrediente')
        for rel in rels:
            total_precio += (rel.ingrediente.costo_unitario * rel.cantidad)

        creado_por = "Desconocido"
        try:
            if r.usuario:
                # Comparar ids (user_id puede venir como str)
                if user_id is not None and int(user_id) == int(getattr(r.usuario, "id", -1)):
                    creado_por = "Tú"
                else:
                    creado_por = r.usuario.user.username if getattr(r.usuario, "user", None) else "Desconocido"
        except Exception:
            # En caso de cualquier inconsistencia, fallback seguro
            creado_por = r.usuario.user.username if getattr(r.usuario, "user", None) else "Desconocido"

        recetas_data.append({
            "receta": r,
            "precio": round(total_precio, 2) if total_precio > 0 else "No calculado"
        })

    return render(
        request,
        "ver_recetas.html",
        {"recetas_data": recetas_data}
    )

def ver_recetas_alumnos(request):
    # Obtener IDs de usuarios que son alumnos (rol contiene alumno/estudiante o ID rol=2 assumption from before)
    # Mejor filtrar por nombre de rol
    alumnos_qs = Usuario.objects.filter(rol__nombre__icontains='estudiante') | \
                 Usuario.objects.filter(rol__nombre__icontains='alumno')
                 # Omitiremos el ID 2 hardcoded para ser más seguros con ORM
    
    recetas_qs = Receta.objects.filter(usuario__in=alumnos_qs).select_related('usuario', 'usuario__user')
    
    # Filtros
    buscar = request.GET.get('buscar', '').strip().lower()
    categoria_filtro = request.GET.get('categoria')
    seccion_filtro = request.GET.get('seccion')
    asignatura_filtro = request.GET.get('asignatura')
    letra = request.GET.get('letra')

    if categoria_filtro and categoria_filtro.lower() != 'todas':
        recetas_qs = recetas_qs.filter(categoria__iexact=categoria_filtro)
        
    if seccion_filtro:
        recetas_qs = recetas_qs.filter(seccion__icontains=seccion_filtro)
        
    if asignatura_filtro:
        recetas_qs = recetas_qs.filter(asignatura__icontains=asignatura_filtro)
        
    if buscar:
        recetas_qs = recetas_qs.filter(nombre__icontains=buscar)
        
    if letra and letra.lower() != 'todas':
        recetas_qs = recetas_qs.filter(nombre__istartswith=letra)

    # Collect categories for filter dropdown
    all_categories = Receta.objects.exclude(categoria__isnull=True).exclude(categoria='').values_list('categoria', flat=True).distinct()
    
    recetas_data = []
    
    for r in recetas_qs:
        # Calcular total
        rels = Receta_Ingrediente.objects.filter(receta=r).select_related('ingrediente')
        subtotal = 0
        for rel in rels:
            subtotal += (rel.cantidad * rel.ingrediente.costo_unitario)
            
        # Comprobante data
        iva_rate = 19
        factor = 1
        comp = Comprobante.objects.filter(receta=r).first()
        if comp:
            iva_rate = comp.iva
            factor = comp.factor_multiplicacion
            
        iva_amount = subtotal * (iva_rate / 100)
        total_con_iva = round((subtotal + iva_amount) * factor, 2)

        recetas_data.append({
            'receta': r,
            'nombre': r.nombre,
            'categoria': r.categoria,
            'tiempo': r.tiempo_preparacion,
            'seccion': r.seccion,
            'asignatura': r.asignatura,
            'precio_subtotal': round(subtotal, 2) if subtotal > 0 else "No calculado",
            'precio': total_con_iva if subtotal > 0 else "No calculado",
            'usuario': r.usuario.user.username if r.usuario and r.usuario.user else 'Desconocido'
        })
        
    return render(request, "ver_recetas_alumnos.html", {
        "recetas_data": recetas_data,
        "categorias": sorted(list(all_categories))
    })

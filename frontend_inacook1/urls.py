from django.urls import path
from .views import (
    auth,
    ingredientes,
    recetas,
    historial,
    unidadmedida,
    perfil,
    comprobantes
    )


urlpatterns = [

    path('', auth.login_view, name='home'),
    path('login/', auth.login_view, name='login'),
    path('register/', auth.register_view, name='register'),
    path('logout/', auth.logout_view, name='logout'),

    path('dashboard/', perfil.dashboard, name='dashboard'),
    path('calculadora/', perfil.calculadora, name='calculadora'),
    path('perfil/', perfil.perfil_view, name='perfil'),
    path('perfil/cambiar-contrasena/', perfil.cambiar_password, name='cambiar_contraseña'),

    path('ingredientes/', ingredientes.ver_ingredientes, name='ver_ingredientes'),
    path('ingredientes/crear/', ingredientes.crear_ingrediente, name='crear_ingrediente'),
    path('ingredientes/editar/<int:id>/', ingredientes.editar_ingrediente, name='editar_ingrediente'),
    path('ingredientes/eliminar/<int:id>/', ingredientes.eliminar_ingrediente, name='eliminar_ingrediente'),

    path('recetas/', recetas.ver_recetas, name='ver_recetas'),
    path('recetas/subir/', recetas.subir_receta, name='subir_receta'),
    path('recetas/editar/<int:id>/', recetas.editar_receta, name='editar_receta'),
    path('recetas/eliminar/<int:id>/', recetas.eliminar_receta, name='eliminar_receta'),
    path('recetas/borrar/<int:id>/', recetas.borrar_receta, name='borrar_receta'),
    path('recetas-alumnos/', recetas.ver_recetas_alumnos, name='ver_recetas_alumnos'),

    path('historial/', historial.ver_historial, name='ver_historial'),

    path('unidades/', unidadmedida.ver_unidades, name='ver_unidades'),

    path('comprobante/<int:id>/', comprobantes.ver_comprobante, name='ver_comprobante'),
]

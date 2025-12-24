from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from inacook.views import (
    ListaIngredientes, 
    DetalleIngrediente, 
    ListaReceta, 
    DetalleReceta,
    ListaUnidadMedicion,
    DetalleUnidadMedicion, 
    ListaComprobante,
    DetalleComprobante,
    ListaHistorial,
    DetalleHistorial,
    ListaUsuario,
    DetalleUsuario,
    ListaRol,
    DetalleRol,
    ListaRecetaIngrediente,
    DetalleRecetaIngrediente,
    CambiarPassword,
)

urlpatterns=[
    path('token-auth/', obtain_auth_token),
    path('change-password/', CambiarPassword.as_view()),
    path('ingredientes/', ListaIngredientes.as_view()),
    path('ingredientes/<int:id>/', DetalleIngrediente.as_view()),
    path('recetas/', ListaReceta.as_view()),
    path('recetas/<int:id>/', DetalleReceta.as_view()),
    path('unidades/', ListaUnidadMedicion.as_view()),
    path('unidades/<int:id>/', DetalleUnidadMedicion.as_view()),
    path('comprobantes/', ListaComprobante.as_view()),
    path('comprobantes/<int:id>/', DetalleComprobante.as_view()),
    path('historial/', ListaHistorial.as_view()),
    path('historial/<int:id>/', DetalleHistorial.as_view()),
    path('usuarios/', ListaUsuario.as_view()),
    path('usuarios/<int:id>/', DetalleUsuario.as_view()),
    path('roles/', ListaRol.as_view()),
    path('roles/<int:id>/', DetalleRol.as_view()),
    path('receta-ingrediente/', ListaRecetaIngrediente.as_view()),
    path('receta-ingrediente/<int:id>/', DetalleRecetaIngrediente.as_view()),
]

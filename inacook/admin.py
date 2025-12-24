from django.contrib import admin
from .models import (
    Rol, 
    Usuario, 
    UnidadMedicion, 
    Ingrediente, 
    Receta, 
    Receta_Ingrediente, 
    Comprobante, 
    Historial
)   

admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(UnidadMedicion)
admin.site.register(Ingrediente)
admin.site.register(Receta)
admin.site.register(Receta_Ingrediente)
admin.site.register(Comprobante)
admin.site.register(Historial)
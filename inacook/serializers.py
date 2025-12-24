from rest_framework import serializers
from inacook.models import (
    Rol, 
    Usuario, 
    UnidadMedicion, 
    Ingrediente, 
    Receta_Ingrediente, 
    Receta, 
    Historial, 
    Comprobante
)


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    nombre_rol = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = '__all__'


class UnidadMedicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadMedicion
        fields = '__all__'


class IngredienteSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.user.username', read_only=True)
    class Meta:
        model = Ingrediente
        fields = '__all__'


class RecetaIngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta_Ingrediente
        fields = '__all__'

class RecetaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.user.username', read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Receta
        fields = '__all__'

class ComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprobante
        fields = '__all__'

class HistorialSerializer(serializers.ModelSerializer):
    receta_nombre = serializers.CharField(source='receta.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.user.username', read_only=True)

    class Meta:
        model = Historial
        fields = '__all__'
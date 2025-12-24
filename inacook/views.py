from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import (
    Rol,
    UnidadMedicion,
    Ingrediente,
    Receta,
    Comprobante,
    Historial,
    Receta_Ingrediente,
    Receta_Ingrediente,
    Usuario,
)

from .serializers import (
    IngredienteSerializer, 
    RecetaSerializer, 
    ComprobanteSerializer, 
    HistorialSerializer,
    RolSerializer,
    UnidadMedicionSerializer,
    RecetaIngredienteSerializer,
    UsuarioSerializer,
)

class ListaIngredientes(APIView):

    def get(self, request):
        
        ingredientes = Ingrediente.objects.none()
        if not request.user.is_authenticated:
            ingredientes = Ingrediente.objects.none()
        else:
            try:
                usuario_actual = Usuario.objects.get(user=request.user)
            except Usuario.DoesNotExist:
                usuario_actual = None

            rol_nombre = ''
            if usuario_actual and usuario_actual.rol:
                rol_nombre = (usuario_actual.rol.nombre or '').lower()

            
            if rol_nombre in ('profesor', 'profesora', 'teacher', 'admin', 'administrador', 'administrator'):
                usuario_id = request.query_params.get('usuario_id')
                if usuario_id:
                    try:
                        target = Usuario.objects.get(id=usuario_id)
                        ingredientes = Ingrediente.objects.filter(usuario=target)
                    except Usuario.DoesNotExist:
                        ingredientes = Ingrediente.objects.none()
                else:
                    ingredientes = Ingrediente.objects.all()
            else:
                
                if usuario_actual:
                    ingredientes = Ingrediente.objects.filter(usuario=usuario_actual)
                else:
                    ingredientes = Ingrediente.objects.none()
        serializer=IngredienteSerializer(ingredientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=IngredienteSerializer(data=request.data)
        if serializer.is_valid():
            
            usuario = None
            if request.user.is_authenticated:
                usuario, _ = Usuario.objects.get_or_create(user=request.user)
            serializer.save(usuario=usuario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetalleIngrediente(APIView):

    def get_object(self, id):
        try:
            return Ingrediente.objects.get(id=id)
        except Ingrediente.DoesNotExist:
            return None

    def get(self, request, id):
        ingrediente=self.get_object(id)
        if not ingrediente:
            return Response({"error": "Ingrediente no encontrado"}, status=404)

        serializer=IngredienteSerializer(ingrediente)
        return Response(serializer.data)

    def put(self, request, id):
        ingrediente=self.get_object(id)
        if not ingrediente:
            return Response({"error": "Ingrediente no encontrado"}, status=404)

        serializer=IngredienteSerializer(ingrediente, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        ingrediente=self.get_object(id)
        if not ingrediente:
            return Response({"error": "Ingrediente no encontrado"}, status=404)

        ingrediente.delete()
        return Response({"mensaje": "Ingrediente eliminado"}, status=204)

class ListaReceta(APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)

    def get(self, request):
    
    
        recetas = Receta.objects.none()
        if not request.user.is_authenticated:
            recetas = Receta.objects.none()
        else:
            try:
                usuario_actual = Usuario.objects.get(user=request.user)
            except Usuario.DoesNotExist:
                usuario_actual = None

            rol_nombre = ''
            if usuario_actual and usuario_actual.rol:
                rol_nombre = (usuario_actual.rol.nombre or '').lower()

            
            if rol_nombre in ('profesor', 'profesora', 'teacher', 'admin', 'administrador', 'administrator'):
                usuario_id = request.query_params.get('usuario_id')
                if usuario_id:
                    try:
                        target = Usuario.objects.get(id=usuario_id)
                        recetas = Receta.objects.filter(usuario=target)
                    except Usuario.DoesNotExist:
                        recetas = Receta.objects.none()
                else:
                    recetas = Receta.objects.all()
            else:
                
                if usuario_actual:
                    recetas = Receta.objects.filter(usuario=usuario_actual)
                else:
                    recetas = Receta.objects.none()
        serializer=RecetaSerializer(recetas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RecetaSerializer(data=request.data)
        if serializer.is_valid():
            
            perfil_usuario = None
            if request.user.is_authenticated:
                perfil_usuario, _ = Usuario.objects.get_or_create(user=request.user)
            
            receta = serializer.save(usuario=perfil_usuario)

            try:
                Historial.objects.create(
                    receta=receta,
                    usuario=perfil_usuario,
                    cambio_realizado="Receta creada"
                )
            except Exception as e:
                print(f"Error historial: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetalleReceta(APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)

    def get_object(self, id):
        try:
            return Receta.objects.get(id=id)
        except Receta.DoesNotExist:
            return None

    def get(self, request, id):
        receta=self.get_object(id)
        if not receta:
            return Response({"error": "Receta no encontrada"}, status=404)

        serializer=RecetaSerializer(receta)
        return Response(serializer.data)

    def put(self, request, id):
        receta=self.get_object(id)
        if not receta:
            return Response({"error": "Receta no encontrada"}, status=404)

        serializer=RecetaSerializer(receta, data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            try:
                usuario_editor = None
                if request.user.is_authenticated:
                    usuario_editor, _ = Usuario.objects.get_or_create(user=request.user)
                
                if not usuario_editor:
                    usuario_editor = receta.usuario

                Historial.objects.create(
                    receta=receta,
                    usuario=usuario_editor,
                    cambio_realizado="Receta editada"
                )
            except Exception as e:
                 print(f"Error historial: {e}")

            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        receta=self.get_object(id)
        if not receta:
            return Response({"error": "Receta no encontrada"}, status=404)

        receta.delete()
        return Response({"mensaje": "Receta eliminada"}, status=204)

class ListaRol(APIView):

    def get(self, request):
        roles=Rol.objects.all()
        serializer=RolSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=RolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DetalleRol(APIView):
    def get_object(self, id):
        try:
            return Rol.objects.get(id=id)
        except Rol.DoesNotExist:
            return None

    def get(self, request, id):
        rol=self.get_object(id)
        if not rol:
            return Response({"error": "Rol no encontrado"}, status=404)
        serializer=RolSerializer(rol)
        return Response(serializer.data)

    def put(self, request, id):
        rol=self.get_object(id)
        if not rol:
            return Response({"error": "Rol no encontrado"}, status=404)
        serializer=RolSerializer(rol, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        rol=self.get_object(id)
        if not rol:
            return Response({"error": "Rol no encontrado"}, status=404)
        rol.delete()
        return Response({"mensaje": "Rol eliminado"}, status=204)


class ListaUnidadMedicion(APIView):
    def get(self, request):
        unidades=UnidadMedicion.objects.all()
        serializer=UnidadMedicionSerializer(unidades, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=UnidadMedicionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetalleUnidadMedicion(APIView):
    def get_object(self, id):
        try:
            return UnidadMedicion.objects.get(id=id)
        except UnidadMedicion.DoesNotExist:
            return None

    def get(self, request, id):
        unidad=self.get_object(id)
        if not unidad:
            return Response({"error": "Unidad no encontrada"}, status=404)
        serializer=UnidadMedicionSerializer(unidad)
        return Response(serializer.data)

    def put(self, request, id):
        unidad=self.get_object(id)
        if not unidad:
            return Response({"error": "Unidad no encontrada"}, status=404)
        serializer=UnidadMedicionSerializer(unidad, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        unidad=self.get_object(id)
        if not unidad:
            return Response({"error": "Unidad no encontrada"}, status=404)
        unidad.delete()
        return Response({"mensaje": "Unidad eliminada"}, status=204)


class ListaComprobante(APIView):

    def get(self, request):
        comprobantes=Comprobante.objects.all()
        serializer=ComprobanteSerializer(comprobantes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=ComprobanteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DetalleComprobante(APIView):

    def get_object(self, id):
        try:
            return Comprobante.objects.get(id=id)
        except Comprobante.DoesNotExist:
            return None

    def get(self, request, id):
        comprobante=self.get_object(id)
        if not comprobante:
            return Response({"error": "Comprobante no encontrado"}, status=404)

        serializer=ComprobanteSerializer(comprobante)
        return Response(serializer.data)

    def put(self, request, id):
        comprobante=self.get_object(id)
        if not comprobante:
            return Response({"error": "Comprobante no encontrado"}, status=404)

        serializer=ComprobanteSerializer(comprobante, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        comprobante=self.get_object(id)
        if not comprobante:
            return Response({"error": "Comprobante no encontrado"}, status=404)

        comprobante.delete()
        return Response({"mensaje": "Comprobante eliminado"}, status=204)

class ListaHistorial(APIView):

    def get(self, request):
        
        historial = Historial.objects.none()
        if not request.user.is_authenticated:
            historial = Historial.objects.none()
        else:
            try:
                usuario_actual = Usuario.objects.get(user=request.user)
            except Usuario.DoesNotExist:
                usuario_actual = None

            rol_nombre = ''
            if usuario_actual and usuario_actual.rol:
                rol_nombre = (usuario_actual.rol.nombre or '').lower()

            if rol_nombre in ('profesor', 'profesora', 'teacher', 'admin', 'administrador', 'administrator'):
                usuario_id = request.query_params.get('usuario_id')
                if usuario_id:
                    try:
                        target = Usuario.objects.get(id=usuario_id)
                        historial = Historial.objects.filter(usuario=target)
                    except Usuario.DoesNotExist:
                        historial = Historial.objects.none()
                else:
                    
                    historial = Historial.objects.all()
            else:
                
                if usuario_actual:
                    historial = Historial.objects.filter(usuario=usuario_actual)
                else:
                    historial = Historial.objects.none()
        serializer=HistorialSerializer(historial, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=HistorialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DetalleHistorial(APIView):

    def get_object(self, id):
        try:
            return Historial.objects.get(id=id)
        except Historial.DoesNotExist:
            return None

    def get(self, request, id):
        registro=self.get_object(id)
        if not registro:
            return Response({"error": "Historial no encontrado"}, status=404)

        serializer=HistorialSerializer(registro)
        return Response(serializer.data)

    def put(self, request, id):
        registro=self.get_object(id)
        if not registro:
            return Response({"error": "Historial no encontrado"}, status=404)

        serializer=HistorialSerializer(registro, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        registro=self.get_object(id)
        if not registro:
            return Response({"error": "Historial no encontrado"}, status=404)

        registro.delete()
        return Response({"mensaje": "Historial eliminado"}, status=204)

class ListaUsuario(APIView):

    def get(self, request):
        usuarios=Usuario.objects.all()
        serializer=UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        rol_id = request.data.get("rol")

        if not username or not password:
             return Response({"error": "Faltan datos"}, status=400)

        try:
            if User.objects.filter(username=username).exists():
                return Response({"error": "El usuario ya existe"}, status=400)

            user = User.objects.create_user(username=username, password=password, email=email)

            
            try:
                if rol_id is not None:
                    rol_obj = Rol.objects.filter(id=rol_id).first()
                    if rol_obj and rol_obj.nombre and rol_obj.nombre.lower() in ("profesor", "profesora", "teacher", "admin"):
                        user.is_staff = True
                        user.is_superuser = True
                        user.save()
            except Exception:
                pass
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        try:
            usuario = Usuario.objects.create(user=user, rol_id=rol_id)
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=201)
        except Exception as e: 
            user.delete()
            return Response({"error": "Error al crear perfil: " + str(e)}, status=400)

class DetalleUsuario(APIView):

    def get_object(self, id):
        try:
            return Usuario.objects.get(id=id)
        except Usuario.DoesNotExist:
            return None

    def get(self, request, id):
        usuario=self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=404)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

    def put(self, request, id):
        usuario=self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=404)

        serializer=UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        usuario=self.get_object(id)
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=404)

        usuario.delete()
        return Response({"mensaje": "Usuario eliminado"}, status=204)

class ListaRecetaIngrediente(APIView):

    def get(self, request):
        relaciones=Receta_Ingrediente.objects.all()
        serializer=RecetaIngredienteSerializer(relaciones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer=RecetaIngredienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DetalleRecetaIngrediente(APIView):

    def get_object(self, id):
        try:
            return Receta_Ingrediente.objects.get(id=id)
        except Receta_Ingrediente.DoesNotExist:
            return None

    def get(self, request, id):
        relacion=self.get_object(id)
        if not relacion:
            return Response({"error": "Relación no encontrada"}, status=404)
        serializer=RecetaIngredienteSerializer(relacion)
        return Response(serializer.data)

    def put(self, request, id):
        relacion=self.get_object(id)
        if not relacion:
            return Response({"error": "Relación no encontrada"}, status=404)

        serializer=RecetaIngredienteSerializer(relacion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        relacion=self.get_object(id)
        if not relacion:
            return Response({"error": "Relación no encontrada"}, status=404)

        relacion.delete()
        return Response({"mensaje": "Relación eliminada"}, status=204)

class CambiarPassword(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user_id or not old_password or not new_password:
            return Response({"error": "Faltan datos"}, status=400)

        try:
            usuario = Usuario.objects.get(id=user_id)
            user = usuario.user
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        if not user.check_password(old_password):
            return Response({"error": "Contraseña actual incorrecta"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"mensaje": "Contraseña actualizada éxito"}, status=200)


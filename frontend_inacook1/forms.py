from django import forms

class RecetaForm(forms.Form):
    Nombre_Receta = forms.CharField(label="Nombre", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Categoria = forms.CharField(label="Categoría", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Aporte_Calorico = forms.IntegerField(label="Aporte Calórico (kcal)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    Tiempo_Preparacion = forms.IntegerField(label="Tiempo de Preparación (min)", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    imagen = forms.ImageField(label="Imagen", required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    Seccion = forms.CharField(label="Sección", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Asignatura = forms.CharField(label="Asignatura", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

class IngredienteForm(forms.Form):
    Nombre_Ingrediente = forms.CharField(label="Nombre del Ingrediente", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Calidad = forms.CharField(label="Calidad", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    Costo_Unitario = forms.IntegerField(label="Costo Unitario", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    Peso = forms.FloatField(label="peso", required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}))
    UnidadMedicion = forms.ChoiceField(label="Unidad de Medición", widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        unidades = kwargs.pop('unidades_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['UnidadMedicion'].choices = unidades

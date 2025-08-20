from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import LibroLeido, Libro, DiarioLector

ESTADOS = [
    ('pendiente', 'Pendiente'),
    ('iniciado', 'Iniciado'),
    ('en_curso', 'En curso'),
    ('finalizado', 'Finalizado'),
    ('abandonado', 'Abandonado'),
]

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class LibroLeidoForm(forms.ModelForm):
    class Meta:
        model = LibroLeido
        exclude = ['usuario']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'autor': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 4}),
            'estado': forms.Select(attrs={'class': 'form-select rounded-3'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control rounded-3'}),
        }


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DiarioLectorForm(forms.ModelForm):
    class Meta:
        model = DiarioLector
        fields = ['libro_leido', 'frase_iconica', 'punto_clave', 'nota_personal', 'puntuacion']
        widgets = {
            'frase_iconica': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'punto_clave': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nota_personal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'libro_leido': forms.Select(attrs={'class': 'form-select'}),
            'puntuacion': forms.HiddenInput(),
        }


class EditarLibroForm(forms.ModelForm):
    class Meta:
        model = LibroLeido
        fields = ['resumen', 'estado', 'fecha_inicio', 'fecha_fin', 'pdf', 'link']
        widgets = {
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }
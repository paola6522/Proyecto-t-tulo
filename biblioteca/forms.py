# Importación de los módulos necesarios para formularios
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Formulario base para registrar usuarios y para autenticación
from django.contrib.auth.models import User # Modelo de usuario de Django
from .models import LibroLeido, Libro, DiarioLector # Modelos creados en tu app
from django.core.exceptions import ValidationError
import re

# Lista de posibles estados que un libro puede tener
ESTADOS = [
    ('pendiente', 'Pendiente'),
    ('iniciado', 'Iniciado'),
    ('en_curso', 'En curso'),
    ('finalizado', 'Finalizado'),
    ('abandonado', 'Abandonado'),
]

class EmailOrUsernameLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o Correo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o correo electrónico'})
    )

# FORMULARIO DE REGISTRO DE USUARIO
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )

    # Lista de nombres reservados (puedes ampliarla)
    RESERVED_USERNAMES = ["admin", "root", "user", "test", "support", "moderator", "staff"]

    def clean_username(self):
        username = self.cleaned_data.get("username")

        # Solo permitir letras, números y algunos símbolos seguros
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("El nombre de usuario contiene caracteres inválidos.")

        # Bloquear nombres reservados
        if username.lower() in self.RESERVED_USERNAMES:
            raise ValidationError("Ese nombre de usuario no está permitido.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        dominio = email.split('@')[-1]

        # Bloquear duplicados
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")

        # Bloquear correos temporales
        if dominio.lower() in ["tempmail.com", "mailinator.com"]:
            raise ValidationError("No se permiten correos temporales.")

        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")

        comunes = ["123456", "password", "qwerty", "admin"]
        if password.lower() in comunes:
            raise ValidationError("La contraseña es demasiado común.")

        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

        if not re.search(r"[A-Z]", password):
            raise ValidationError("Debe contener al menos una letra mayúscula.")

        if not re.search(r"[a-z]", password):
            raise ValidationError("Debe contener al menos una letra minúscula.")

        if not re.search(r"\d", password):
            raise ValidationError("Debe contener al menos un número.")

        if not re.search(r"[^\w\s]|_", password):  
            raise ValidationError("Debe contener al menos un carácter especial (ej. !, @, #, $, %, &, *, ?, _, -).")

        if re.search(r"(.)\1\1", password):  
            raise ValidationError("No puede contener más de 3 caracteres iguales seguidos.")

        return password

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


#FORMULARIO PARA REGISTRAR UN LIBRO LEÍDO
class LibroLeidoForm(forms.ModelForm):
    class Meta:
        model = LibroLeido # Modelo correspondiente
        exclude = ['usuario'] # El usuario se asigna automáticamente, no se muestra en el formulario
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'autor': forms.TextInput(attrs={'class': 'form-control rounded-3'}),
            'categoria': forms.SelectMultiple(attrs={'class': 'form-select'}), # Selección múltiple de géneros
            'resumen': forms.Textarea(attrs={'class': 'form-control rounded-3', 'rows': 4}), # Resumen del libro
            'estado': forms.Select(attrs={'class': 'form-select rounded-3'}), # Estado del libro (iniciado, finalizado, etc.)
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), # Fecha de inicio
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), # Fecha de fin
            'pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}), # Opción para subir archivo
            'link': forms.URLInput(attrs={'class': 'form-control rounded-3'}), # Link externo del libro
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        # Validar fechas
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de término no puede ser anterior a la fecha de inicio.")
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get("titulo").strip()
        if len(titulo) < 2:
            raise ValidationError("El título debe tener al menos 2 caracteres.")
        return titulo

    def clean_autor(self):
        autor = self.cleaned_data.get("autor").strip()
        if len(autor) < 2:
            raise ValidationError("El autor debe tener al menos 2 caracteres.")
        return autor

    def clean_resumen(self):
        resumen = self.cleaned_data.get("resumen")
        if resumen and len(resumen) < 10:
            raise ValidationError("El resumen es demasiado corto, escribe al menos 10 caracteres.")
        return resumen

    def clean_link(self):
        link = self.cleaned_data.get("link")
        if link and not (link.startswith("http://") or link.startswith("https://")):
            raise ValidationError("El enlace debe comenzar con http:// o https://")
        return link

#FORMULARIO PARA AÑADIR LIBROS A LA BIBLIOTECA
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro # Modelo correspondiente
        fields = ['titulo', 'autor', 'categoria'] # Campos del formulario
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.SelectMultiple(attrs={'class': 'form-select'}),  # Permite seleccionar múltiples categorías
        }

#FORMULARIO PARA EL DIARIO LECTOR 
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

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)  # Sacamos el usuario desde la vista
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['libro_leido'].queryset = LibroLeido.objects.filter(usuario=usuario)



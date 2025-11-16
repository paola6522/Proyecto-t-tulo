# Importación de los módulos necesarios para formularios
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Formulario base para registrar usuarios y para autenticación
from django.contrib.auth.models import User # Modelo de usuario de Django
from .models import LibroLeido, Categoria, DiarioLector # Modelos creados en tu app
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

GENEROS_PREDEFINIDOS = [
    "Acción", "Aventura", "Comedia", "Drama", "Romance", "Fantasía",
    "Ciencia Ficción", "Misterio", "Thriller", "Horror", "Histórico",
    "Bélico", "Psicológico", "Magia", "Sobrenatural", "Distopía",
    "Escolar", "Reencarnación", "Vida cotidiana", "Mitología",
    "Viajes en el tiempo", "LGTB+", "Realismo mágico", "Juvenil",
    "Adulto", "Cuentos", "Manga/Manhwa", "Isekai", "Ensayo",
]

class EmailOrUsernameLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o Correo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario o correo electrónico'
        })
    )

# FORMULARIO DE REGISTRO DE USUARIO
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )

    # Lista de nombres reservados
    RESERVED_USERNAMES = ["admin", "root", "user", "test", "support", "moderator", "staff"]

    def clean_username(self):
        username = self.cleaned_data.get("username") or ""

        # Solo permitir letras, números y algunos símbolos seguros
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("El nombre de usuario contiene caracteres inválidos.")

        # Bloquear nombres reservados
        if username.lower() in self.RESERVED_USERNAMES:
            raise ValidationError("Ese nombre de usuario no está permitido.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email") or ""

        # Si por alguna razón llega vacío, que lo trate como error de campo requerido
        if not email:
            raise ValidationError("Debes ingresar un correo electrónico.")

        dominio = email.split('@')[-1]

        # Bloquear duplicados
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado.")

        # Bloquear correos temporales
        if dominio.lower() in ["tempmail.com", "mailinator.com"]:
            raise ValidationError("No se permiten correos temporales.")

        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1") or ""

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
            raise ValidationError(
                "Debe contener al menos un carácter especial (ej. !, @, #, $, %, &, *, ?, _, -)."
            )

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
    # Declaramos el campo usando ModelMultipleChoiceField
    categoria = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.none(),   # se rellena en __init__
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",
            "size": 6,  # para que se vean varias a la vez
        }),
        label="Categoría",
    )

    class Meta:
        model = LibroLeido
        exclude = ["usuario"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control rounded-3",
            }),
            "autor": forms.TextInput(attrs={
                "class": "form-control rounded-3",
            }),
            "isbn": forms.TextInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "Opcional. Ej: 9788478884452",
            }),
            # 👇 OJO: aquí ya NO pongas widget para 'categoria'
            "resumen": forms.Textarea(attrs={
                "class": "form-control rounded-3",
                "rows": 4,
            }),
            "estado": forms.Select(attrs={
                "class": "form-select rounded-3",
            }),
            "fecha_inicio": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"}
            ),
            "pdf": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "link": forms.URLInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "Opcional. http:// o https://",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1) Aseguramos que existan las categorías en BD
        for nombre in GENEROS_PREDEFINIDOS:
            Categoria.objects.get_or_create(nombre=nombre)

        # 2) Asignamos el queryset actualizado al campo
        self.fields["categoria"].queryset = Categoria.objects.all().order_by("nombre")

    
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



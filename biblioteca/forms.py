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

CATEGORIA_CHOICES = [
    ("Acción", "Acción"),
    ("Aventura", "Aventura"),
    ("Comedia", "Comedia"),
    ("Drama", "Drama"),
    ("Romance", "Romance"),
    ("Fantasía", "Fantasía"),
    ("Ciencia Ficción", "Ciencia Ficción"),
    ("Misterio", "Misterio"),
    ("Thriller", "Thriller"),
    ("Horror", "Horror"),
    ("Histórico", "Histórico"),
    ("Bélico", "Bélico"),
    ("Psicológico", "Psicológico"),
    ("Magia", "Magia"),
    ("Sobrenatural", "Sobrenatural"),
    ("Distopía", "Distopía"),
    ("Escolar", "Escolar"),
    ("Reencarnación", "Reencarnación"),
    ("Vida cotidiana", "Vida cotidiana"),
    ("Mitología", "Mitología"),
    ("Viajes en el tiempo", "Viajes en el tiempo"),
    ("LGTB+", "LGTB+"),
    ("Realismo mágico", "Realismo mágico"),
    ("Juvenil", "Juvenil"),
    ("Adulto", "Adulto"),
    ("Cuentos", "Cuentos"),
    ("Manga/Manhwa", "Manga/Manhwa"),
    ("Isekai", "Isekai"),
    ("Ensayo", "Ensayo"),
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
        model = LibroLeido
        exclude = ['usuario']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
            }),
            'autor': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Opcional. Ej: 9788478884452',
            }),
            'categoria': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 6,
            }),
            'resumen': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 4,
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select rounded-3',
            }),
            'fecha_inicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fecha_fin': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Opcional. http:// o https://',
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # formatos válidos desde el input
        self.fields['fecha_inicio'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin'].input_formats = ['%Y-%m-%d']

        # 🔹 IMPORTANTE: solo seteamos initial cuando NO es formulario enviado (GET, no POST)
        if not self.is_bound and self.instance and self.instance.pk:
            if self.instance.fecha_inicio:
                self.initial['fecha_inicio'] = self.instance.fecha_inicio.strftime('%Y-%m-%d')
            if self.instance.fecha_fin:
                self.initial['fecha_fin'] = self.instance.fecha_fin.strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        fi = cleaned_data.get("fecha_inicio")
        ff = cleaned_data.get("fecha_fin")
        if fi and ff and ff < fi:
            raise ValidationError("La fecha de término no puede ser anterior a la fecha de inicio.")
        return cleaned_data

    def clean_titulo(self):
        t = (self.cleaned_data.get("titulo") or "").strip()
        if len(t) < 2:
            raise ValidationError("El título debe tener al menos 2 caracteres.")
        return t

    def clean_autor(self):
        a = (self.cleaned_data.get("autor") or "").strip()
        if len(a) < 2:
            raise ValidationError("El autor debe tener al menos 2 caracteres.")
        return a

    def clean_resumen(self):
        r = self.cleaned_data.get("resumen")
        if r and len(r.strip()) < 10:
            raise ValidationError("El resumen es demasiado corto, escribe al menos 10 caracteres.")
        return r

    def clean_link(self):
        link = self.cleaned_data.get("link")
        if link and not (link.startswith("http://") or link.startswith("https://")):
            raise ValidationError("El enlace debe comenzar con http:// o https://")
        return link

    def clean_isbn(self):
        isbn = (self.cleaned_data.get("isbn") or "").strip()
        if not isbn:
            return ""
        normalized = isbn.replace("-", "").replace(" ", "")
        if not normalized.isdigit():
            raise ValidationError("El ISBN debe contener solo números (puedes usar guiones o espacios).")
        if len(normalized) not in (10, 13):
            raise ValidationError("El ISBN debe tener 10 o 13 dígitos.")
        return normalized

    
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



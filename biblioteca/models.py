from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

# ------------------------
# Lista de opciones de estado
# ------------------------
ESTADO_LIBRO = [
    ('pendiente', 'Pendiente'),
    ('iniciado', 'Iniciado'),
    ('en_curso', 'En curso'),
    ('finalizado', 'Finalizado'),
    ('abandonado', 'Abandonado'),
]

# ------------------------
# Modelo Categoría (Género literario)
# ------------------------
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, db_index=True)  # índice para búsquedas rápidas

    def __str__(self):
        return self.nombre


# ------------------------
# Modelo Libro (catálogo de libros agregados por usuario)
# ------------------------
class Libro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # se elimina con el usuario
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    categoria = models.ManyToManyField(Categoria, blank=True)  # categorías opcionales

    def __str__(self):
        return self.titulo


# ------------------------
# Modelo LibroLeido (libros en la biblioteca personal)
# ------------------------
def validar_pdf(value):
    """Valida que el archivo sea PDF y no pese más de 5 MB."""
    if value.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("El archivo no puede superar los 5 MB.")

class LibroLeido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200, default="Sin título")
    autor = models.CharField(max_length=100, default="Desconocido")
    categoria = models.ManyToManyField(Categoria, blank=True)
    resumen = models.TextField(max_length=2000, blank=True)  # límite para evitar textos enormes
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_LIBRO,
        default='pendiente'
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    pdf = models.FileField(
        upload_to='libros/',
        null=True, blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),  # solo PDF
            validar_pdf
        ]
    )
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo


# ------------------------
# Modelo DiarioLector (notas del usuario)
# ------------------------
class DiarioLector(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro_leido = models.ForeignKey(LibroLeido, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    puntuacion = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]  # puntuación segura 0–5
    )
    frase_iconica = models.TextField(blank=True, max_length=500)
    punto_clave = models.TextField(blank=True, max_length=1000)
    nota_personal = models.TextField(blank=True, max_length=2000)

    def __str__(self):
        return f"Entrada {self.fecha} - {self.libro_leido.titulo}"


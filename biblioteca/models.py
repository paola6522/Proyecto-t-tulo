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
    nombre = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.nombre


# ------------------------
# Modelo Libro (catálogo de libros agregados por usuario)
# (opcional, útil si luego quieres normalizar tu biblioteca)
# ------------------------
class Libro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    # Para enlazar con el dataset del recomendador (opcional pero MUY útil)
    isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text="Opcional. Úsalo si conoces el ISBN para mejores recomendaciones."
    )
    categoria = models.ManyToManyField(Categoria, blank=True)

    def __str__(self):
        return self.titulo


# ------------------------
# Validador PDF
# ------------------------
def validar_pdf(value):
    if value.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("El archivo no puede superar los 5 MB.")


# ------------------------
# Modelo LibroLeido (biblioteca personal del usuario)
# ------------------------
class LibroLeido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Datos básicos del libro
    titulo = models.CharField(max_length=200, default="Sin título")
    autor = models.CharField(max_length=100, default="Desconocido")
    # ISBN opcional para enganchar con el modelo KNN
    isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_index=True,
        help_text="Opcional. Si existe, se usa para mejorar las recomendaciones."
    )
    categoria = models.ManyToManyField(Categoria, blank=True)

    # Info de lectura
    resumen = models.TextField(max_length=2000, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_LIBRO,
        default='pendiente'
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    # Archivos / links
    pdf = models.FileField(
        upload_to='libros/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validar_pdf
        ]
    )
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo


# ------------------------
# Modelo DiarioLector (notas, puntuaciones del usuario)
# ------------------------
class DiarioLector(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro_leido = models.ForeignKey(LibroLeido, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    puntuacion = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    frase_iconica = models.TextField(blank=True, max_length=500)
    punto_clave = models.TextField(blank=True, max_length=1000)
    nota_personal = models.TextField(blank=True, max_length=2000)

    def __str__(self):
        return f"Entrada {self.fecha} - {self.libro_leido.titulo}"


# ------------------------
# Modelo Pendiente (lista de deseos / “quiero leer”)
# ------------------------
class Pendiente(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Guardamos lo suficiente para reconstruir la tarjeta desde las recomendaciones
    isbn = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evitar duplicados del mismo libro para el mismo usuario
        unique_together = ('usuario', 'isbn', 'titulo')

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"



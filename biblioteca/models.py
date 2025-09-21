from django.db import models
from django.contrib.auth.models import User # Importamos el modelo de usuarios de Django

# LISTA DE OPCIONES PARA EL ESTADO DEL LIBRO
ESTADO_LIBRO = [
    ('pendiente', 'Pendiente'),
    ('iniciado', 'Iniciado'),
    ('en_curso', 'En curso'),
    ('finalizado', 'Finalizado'),
    ('abandonado', 'Abandonado'),
]

# MODELO CATEGORÍA (GÉNERO LITERARIO)
class Categoria(models.Model):
    # Nombre único de la categoría (ej: Fantasía, Romance, Ciencia Ficción)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre # Se mostrará el nombre al representar el objeto como texto

# MODELO LIBRO (CATÁLOGO GENERAL DE LIBROS)
class Libro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario que añadió el libro
    titulo = models.CharField(max_length=200) # Título del libro
    autor = models.CharField(max_length=100)   # Autor del libro
    categoria = models.ManyToManyField(Categoria) # Relación muchos a muchos con categorías

    def __str__(self):
        return self.titulo # Representación legible del libro
    
# MODELO LIBRO LEÍDO (PERSONAL DE CADA USUARIO)
class LibroLeido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario que leyó el libro
    titulo = models.CharField(max_length=200, default="Sin título")  # Título personalizado (editable)
    autor = models.CharField(max_length=100, default="Desconocido")  # Autor del libro
    categoria = models.ManyToManyField(Categoria, blank=True)  # Categorías asociadas
    resumen = models.TextField() # Breve descripción del contenido o experiencia lectora
    estado = models.CharField(max_length=20, choices=ESTADO_LIBRO) # Estado de lectura
    fecha_inicio = models.DateField(null=True, blank=True) # Fecha en que se comenzó el libro
    fecha_fin = models.DateField(null=True, blank=True) # Fecha en que se terminó el libro
    pdf = models.FileField(upload_to='libros/', null=True, blank=True) # Archivo PDF del libro (opcional)
    link = models.URLField(blank=True, null=True) # Enlace al libro en línea (opcional)

    def __str__(self):
        return self.titulo # Mostrar título en listados y admin

# MODELO DIARIO LECTOR (REGISTRO PERSONAL DE NOTAS)
class DiarioLector(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario dueño del diario
    libro_leido = models.ForeignKey(LibroLeido, on_delete=models.CASCADE) # Libro al que pertenece la entrada
    fecha = models.DateField(auto_now_add=True) # Fecha de la entrada (se asigna automáticamente al crear)
    puntuacion = models.IntegerField(default=0) #Puntuación del libro de 0 a 5
    frase_iconica = models.TextField(blank=True) # Frase memorable o cita del libro
    punto_clave = models.TextField(blank=True) # Momento o idea central del libro
    nota_personal = models.TextField(blank=True) # Reflexión o comentario personal sobre la lectura

    def __str__(self):
        # Muestra la entrada con fecha y título del libro leído
        return f"Entrada de {self.fecha} - {self.libro_leido.libro.titulo}"

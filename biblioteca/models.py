from django.db import models
from django.contrib.auth.models import User

ESTADO_LIBRO = [
    ('pendiente', 'Pendiente'),
    ('leyendo', 'Leyendo'),
    ('finalizado', 'Finalizado'),
    ('abandonado', 'Abandonado'),
]

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)        # Agregado
    categoria = models.CharField(max_length=100)    # Agregado

    def __str__(self):
        return self.titulo

class LibroLeido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200, default="Sin título") 
    autor = models.CharField(max_length=100, default="Desconocido")  # o ForeignKey si tienes modelo Autor
    categoria = models.CharField(max_length=100, default="Sin categoría")  # o ManyToManyField si quieres varias
    resumen = models.TextField()
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('iniciado', 'Iniciado'),
        ('en_curso', 'En curso'),
        ('finalizado', 'Finalizado'),
        ('abandonado', 'Abandonado'),
    ])
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    pdf = models.FileField(upload_to='libros/', null=True, blank=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo


class DiarioLector(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro_leido = models.ForeignKey(LibroLeido, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    puntuacion = models.IntegerField(default=0) #Puntuación del libro de 0 a 5
    frase_iconica = models.TextField(blank=True)
    punto_clave = models.TextField(blank=True)
    nota_personal = models.TextField(blank=True)

    def __str__(self):
        return f"Entrada de {self.fecha} - {self.libro_leido.libro.titulo}"

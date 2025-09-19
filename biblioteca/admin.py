from django.contrib import admin
from biblioteca.models import Libro, Categoria, LibroLeido, DiarioLector
#Register your models here.
admin.site.register(Categoria)
admin.site.register(Libro)
admin.site.register(LibroLeido)
admin.site.register(DiarioLector)

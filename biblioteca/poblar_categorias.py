# biblioteca/poblar_categorias.py
from .models import Categoria

generos = [
    "Acción", "Aventura", "Comedia", "Drama", "Romance", "Fantasía",
    "Ciencia Ficción", "Misterio", "Thriller", "Horror", "Histórico",
    "Bélico", "Psicológico", "Magia", "Sobrenatural", "Distopía",
    "Escolar", "Reencarnación", "Vida cotidiana", "Mitología", 
    "Viajes en el tiempo", "LGTB+", "Realismo mágico", "Juvenil",
    "Adulto", "Cuentos", "Manga/Manhwa", "Isekai", "Ensayo"
]

def poblar():
    for genero in generos:
        Categoria.objects.get_or_create(nombre=genero)
    print("Categorías pobladas correctamente.")

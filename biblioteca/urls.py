from django.urls import path
from . import views # Importa las vistas definidas en views.py
from django.contrib.auth.views import LogoutView # Vista genérica de Django para cerrar sesión
from .views import registro_view # Importación explícita de la vista personalizada de registro
from django.contrib.auth import views as auth_views # Alias para usar vistas de autenticación

urlpatterns = [
    path('', views.inicio, name='inicio'), # Página de inicio
    path('biblioteca/', views.biblioteca, name='biblioteca'), # Biblioteca personal del usuario (libros leídos)
    path('diario/', views.diario_lector, name='diario_lector'), # Diario lector (notas, frases y reflexiones personales)
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'), # Recomendaciones de libros con IA
    path('libro/<int:pk>/', views.ver_libro, name='ver_libro'), # Ver detalles de un libro leído (por ID)
    path('editar-libro/<int:pk>/', views.editar_libro, name='editar_libro'), # Editar detalles de un libro leído
    path('eliminar/<int:pk>/', views.eliminar_libro, name='eliminar_libro'), # Eliminar libro desde la biblioteca (uso de ID)
    path('biblioteca/agregar/', views.agregar_libro_leido, name='agregar_libro'), # Agregar un nuevo libro leído a la biblioteca
    path('agregar-entrada/', views.agregar_entrada, name='agregar_entrada'),# Duplicada hay que verificar que es lo quehace si se borra se cae la pagina # Agregar una nueva entrada al diario lector (nota, puntuación, etc.)
    path('eliminar-entrada/<int:pk>/', views.eliminar_entrada, name='eliminar_entrada'), # Eliminar una entrada del diario lector
    path('editar-entrada/<int:pk>/', views.editar_entrada, name='editar_entrada'), # Editar entrada del diario lector
    path('agregar-entrada/', views.agregar_entrada, name='agregar_diario'),# Duplicada hay que verificar que es lo quehace si se borra se cae la pagina # Agregar una nueva entrada al diario lector (nota, puntuación, etc.)
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'), # Cerrar sesión del usuario (usa vista genérica de Django)
    path('registro/', registro_view, name='registro'), # Registro personalizado de usuario
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), # Inicio de sesión con plantilla personalizada
    path('estadisticas/', views.estadisticas, name='estadisticas'), # Página de estadísticas de lectura (gráficos, totales, etc.)
]

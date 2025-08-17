from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import registro_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
    path('diario/', views.diario_lector, name='diario_lector'),
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'),
    path('libro/<int:pk>/', views.ver_libro, name='ver_libro'),
    path('biblioteca/eliminar/<int:pk>/', views.eliminar_libro, name='eliminar_libro'),
    path('editar-libro/<int:pk>/', views.editar_libro, name='editar_libro'),
    path('eliminar/<int:pk>/', views.eliminar_libro, name='eliminar_libro'),
    path('biblioteca/agregar/', views.agregar_libro_leido, name='agregar_libro'),
    path('agregar-entrada/', views.agregar_entrada, name='agregar_entrada'),
    path('eliminar-entrada/<int:pk>/', views.eliminar_entrada, name='eliminar_entrada'),
    path('editar-entrada/<int:pk>/', views.editar_entrada, name='editar_entrada'),
    path('agregar-entrada/', views.agregar_entrada, name='agregar_diario'),
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'),
    path('registro/', registro_view, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
]

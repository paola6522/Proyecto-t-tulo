from django.shortcuts import render, redirect, get_object_or_404
from .models import Libro, LibroLeido, DiarioLector
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import RegistroUsuarioForm, LibroLeidoForm, DiarioLectorForm, LibroForm, EditarLibroForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings


import os
import joblib
import pandas as pd

def inicio(request):
    return render(request, 'inicio.html')

@login_required
def biblioteca(request):
    libros = LibroLeido.objects.filter(usuario=request.user)  # o Libro.objects.all() según tu modelo
    return render(request, 'biblioteca/biblioteca.html', {'libros': libros})

@login_required
def agregar_libro_leido(request):
    if request.method == 'POST':
        form = LibroLeidoForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            libro.usuario = request.user  # ✅ Asignar usuario logueado
            libro.save()
            messages.success(request, 'Libro agregado correctamente.')
            return redirect('biblioteca')
    else:
        form = LibroLeidoForm()
    return render(request, 'biblioteca/agregar_libro_leido.html', {'form': form})

@login_required
def ver_libro(request, pk):
    libro = get_object_or_404(LibroLeido, pk=pk)
    return render(request, 'biblioteca/ver_libro.html', {'libro': libro})

@login_required
def eliminar_libro(request, pk):
    libro = get_object_or_404(LibroLeido, pk=pk, usuario=request.user)
    if request.method == 'POST':
        libro.delete()
        return redirect('biblioteca')
    return render(request, 'biblioteca/eliminar_libro.html', {'libro': libro})

@login_required
def editar_libro(request, pk):
    libro_leido = get_object_or_404(LibroLeido, pk=pk)
    if request.method == 'POST':
        form = LibroLeidoForm(request.POST, request.FILES, instance=libro_leido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado correctamente.')
            return redirect('biblioteca')
    else:
        form = LibroLeidoForm(instance=libro_leido)
    return render(request, 'biblioteca/editar_libro.html', {'form': form})


@login_required
def diario_lector(request):
    diarios = DiarioLector.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'biblioteca/diario_lector.html', {'diarios': diarios})


@login_required
def agregar_entrada(request):
    libro_id = request.GET.get('libro_id')
    if request.method == 'POST':
        form = DiarioLectorForm(request.POST, request.FILES)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user  # si tienes campo usuario
            entrada.save()
            messages.success(request, 'Entrada agregada al diario lector.')
            return redirect('diario_lector')
    else:
        form = DiarioLectorForm(initial={'libro_leido': libro_id})
    return render(request, 'biblioteca/agregar_diario.html', {'form': form})

@login_required
def eliminar_entrada(request, pk):
    entrada = get_object_or_404(DiarioLector, pk=pk)
    entrada.delete()
    messages.success(request, 'Entrada eliminada del diario.')
    return redirect('diario_lector')

@login_required
def editar_entrada(request, pk):
    entrada = get_object_or_404(DiarioLector, pk=pk)

    if request.method == 'POST':
        form = DiarioLectorForm(request.POST, instance=entrada)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada actualizada correctamente.')
            return redirect('diario_lector')
    else:
        form = DiarioLectorForm(instance=entrada)

    return render(request, 'biblioteca/editar_entrada.html', {'form': form, 'entrada': entrada})

@login_required
def recomendaciones(request):
    modelo_path = os.path.join(settings.BASE_DIR, 'modelo_recomendador.pkl')
    matriz_path = os.path.join(settings.BASE_DIR, 'pivot_matrix.pkl')
    info_path = os.path.join(settings.BASE_DIR, 'info_libros.pkl')

    model_knn = joblib.load(modelo_path)
    pivot = pd.read_pickle(matriz_path)
    libros_info = joblib.load(info_path)

    libro_seleccionado = request.GET.get('libro')
    if not libro_seleccionado or libro_seleccionado not in pivot.index:
        libro_seleccionado = pivot.index[0]

    libro_index = pivot.index.get_loc(libro_seleccionado)
    distancias, indices = model_knn.kneighbors(pivot.iloc[libro_index, :].values.reshape(1, -1), n_neighbors=6)

    libros_recomendados = []
    for i in indices.flatten()[1:]:
        titulo = pivot.index[i]
        autor = libros_info.get(titulo, "Autor desconocido")
        libros_recomendados.append({'titulo': titulo, 'autor': autor})

    return render(request, 'biblioteca/recomendaciones.html', {
        'libro_base': libro_seleccionado,
        'recomendaciones': libros_recomendados,
        'libros_disponibles': pivot.index.tolist()
    })


def registro_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)  # Inicia sesión automáticamente
            return redirect('inicio')  # O redirige donde desees
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'registration/registro.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('inicio')

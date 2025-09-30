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
from django.db.models import Count, Q
from collections import defaultdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json



import os
import joblib
import pandas as pd


def inicio(request):
    return render(request, 'inicio.html')


@login_required
def biblioteca(request):
    query = request.GET.get('q')
    
    if query:
        libros = LibroLeido.objects.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(categoria__nombre__icontains=query),
            usuario=request.user
        ).distinct()
    else:
        libros = LibroLeido.objects.filter(usuario=request.user)
    
    return render(request, 'biblioteca/biblioteca.html', {
        'libros': libros,
        'query': query  # por si quieres mantener el texto buscado en el input
    })

@login_required
def agregar_libro_leido(request):
    if request.method == 'POST':
        form = LibroLeidoForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            libro.usuario = request.user  # Asignar usuario logueado
            libro.save()
            form.save_m2m()
            messages.success(request, '¡Libro registrado exitosamente!')
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
    query = request.GET.get('q')
    diarios = DiarioLector.objects.filter(usuario=request.user)

    if query:
        diarios = diarios.filter(
            Q(libro_leido__titulo__icontains=query) |
            Q(libro_leido__autor__icontains=query)
        )

    return render(request, 'biblioteca/diario_lector.html', {'diarios': diarios})


@login_required
def agregar_entrada(request):
    libro_id = request.GET.get('libro_id')
    if request.method == 'POST':
        form = DiarioLectorForm(request.POST, request.FILES, usuario=request.user)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user  # si tienes campo usuario
            entrada.save()
            messages.success(request, 'Entrada agregada al diario lector.')
            return redirect('diario_lector')
    else:
        form = DiarioLectorForm(initial={'libro_leido': libro_id}, usuario=request.user)
    return render(request, 'biblioteca/agregar_diario.html', {'form': form})

@login_required
def eliminar_entrada(request, pk):
    entrada = get_object_or_404(DiarioLector, pk=pk, usuario=request.user)
    if request.method == 'POST':
        entrada.delete()
        messages.success(request, 'Entrada eliminada del diario.')
        return redirect('diario_lector')
    return render(request, 'biblioteca/eliminar_entrada.html', {'entrada': entrada})

@login_required
def editar_entrada(request, pk):
    entrada = get_object_or_404(DiarioLector, pk=pk, usuario=request.user)

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


def inicio(request):
    return render(request, 'inicio.html')


def registro_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('inicio')
        else:
            print("Errores del formulario:", form.errors)  # 👈 Debug
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'registration/registro.html', {'form': form})


@login_required
def estadisticas(request):
    usuario = request.user

    # Gráfico de pastel por estado
    resumen = LibroLeido.objects.filter(usuario=usuario) \
        .values('estado') \
        .annotate(total=Count('estado'))

    etiquetas = [item['estado'] for item in resumen]
    cantidades = [item['total'] for item in resumen]

    # Gráfico de líneas por mes y estado
    libros = LibroLeido.objects.filter(usuario=usuario, fecha_inicio__isnull=False)

    meses_set = set()
    estado_mensual = defaultdict(lambda: defaultdict(int))  # estado_mensual[estado][mes] = cantidad

    for libro in libros:
        estado = libro.estado
        inicio = libro.fecha_inicio
        fin = libro.fecha_fin if libro.fecha_fin else date.today()

        # Para libros iniciados o en curso: contar mes a mes
        if estado in ['iniciado', 'en_curso']:
            mes_actual = inicio.replace(day=1)
            while mes_actual <= fin:
                mes_str = mes_actual.strftime('%b %Y')
                estado_mensual[estado][mes_str] += 1
                meses_set.add(mes_str)
                mes_actual += relativedelta(months=1)

        # Para finalizados: contar solo en mes de inicio
        elif estado == 'finalizado':
            mes_str = inicio.strftime('%b %Y')
            estado_mensual[estado][mes_str] += 1
            meses_set.add(mes_str)

    # Ordenar meses cronológicamente
    meses_ordenados = sorted(meses_set, key=lambda m: datetime.strptime(m, '%b %Y'))

    # Convertir a JSON
    datos_linea = {
        estado: [estado_mensual[estado].get(mes, 0) for mes in meses_ordenados]
        for estado in ['iniciado', 'en_curso', 'finalizado']
    }

    return render(request, 'biblioteca/estadisticas.html', {
        'etiquetas': etiquetas,
        'cantidades': cantidades,
        'meses': json.dumps(meses_ordenados),
        'datos_linea': json.dumps(datos_linea),
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Libro, LibroLeido, DiarioLector, Pendiente
from .forms import RegistroUsuarioForm, LibroLeidoForm, DiarioLectorForm

from collections import defaultdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json

# Import del recomendador KNN item-item
from .recomendaciones import recomendar_para_usuario

# ------------------------
# INICIO
# ------------------------
def inicio(request):
    return render(request, 'inicio.html')


# ------------------------
# REGISTRO DE USUARIO
# ------------------------
def registro_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, 'Tu cuenta ha sido creada con éxito. 💕')
            return redirect('inicio')
        else:
            # Para debug en desarrollo
            print("Errores del formulario:", form.errors)
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registration/registro.html', {'form': form})


# ------------------------
# BIBLIOTECA (Listado de libros del usuario)
# ------------------------
@login_required
def biblioteca(request):
    query = request.GET.get('q', '')

    libros = LibroLeido.objects.filter(usuario=request.user)

    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(categoria__nombre__icontains=query)
        ).distinct()

    return render(request, 'biblioteca/biblioteca.html', {
        'libros': libros,
        'query': query,
    })


# ------------------------
# AGREGAR LIBRO LEÍDO
# ------------------------
@login_required
def agregar_libro_leido(request):
    if request.method == 'POST':
        form = LibroLeidoForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            libro.usuario = request.user
            libro.save()
            form.save_m2m()
            messages.success(request, '¡Libro registrado exitosamente en tu biblioteca! 📚')
            return redirect('biblioteca')
    else:
        form = LibroLeidoForm()

    return render(request, 'biblioteca/agregar_libro_leido.html', {'form': form})


# ------------------------
# VER DETALLE LIBRO
# ------------------------
@login_required
def ver_libro(request, pk):
    libro = get_object_or_404(LibroLeido, pk=pk, usuario=request.user)
    return render(request, 'biblioteca/ver_libro.html', {'libro': libro})


# ------------------------
# EDITAR LIBRO
# ------------------------
@login_required
def editar_libro(request, pk):
    libro_leido = get_object_or_404(LibroLeido, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = LibroLeidoForm(request.POST, request.FILES, instance=libro_leido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado correctamente. ✨')
            return redirect('biblioteca')
    else:
        form = LibroLeidoForm(instance=libro_leido)

    return render(request, 'biblioteca/editar_libro.html', {'form': form, 'libro': libro_leido})

# ------------------------
# ELIMINAR LIBRO
# ------------------------
@login_required
def eliminar_libro(request, pk):
    libro = get_object_or_404(LibroLeido, pk=pk, usuario=request.user)

    if request.method == 'POST':
        libro.delete()
        messages.success(request, 'Libro eliminado de tu biblioteca.')
        return redirect('biblioteca')

    return render(request, 'biblioteca/eliminar_libro.html', {'libro': libro})


# ------------------------
# DIARIO LECTOR - LISTADO
# ------------------------
@login_required
def diario_lector(request):
    query = request.GET.get('q', '')

    diarios = DiarioLector.objects.filter(usuario=request.user)

    if query:
        diarios = diarios.filter(
            Q(libro_leido__titulo__icontains=query) |
            Q(libro_leido__autor__icontains=query)
        )

    return render(request, 'biblioteca/diario_lector.html', {
        'diarios': diarios,
        'query': query,
    })


# ------------------------
# AGREGAR ENTRADA DIARIO
# ------------------------
@login_required
def agregar_entrada(request):
    libro_id = request.GET.get('libro_id')

    if request.method == 'POST':
        form = DiarioLectorForm(request.POST, usuario=request.user)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user
            entrada.save()
            messages.success(request, 'Entrada agregada al diario lector. 📝')
            return redirect('diario_lector')
    else:
        form = DiarioLectorForm(initial={'libro_leido': libro_id}, usuario=request.user)

    return render(request, 'biblioteca/agregar_diario.html', {'form': form})


# ------------------------
# EDITAR ENTRADA DIARIO
# ------------------------
@login_required
def editar_entrada(request, pk):
    entrada = get_object_or_404(DiarioLector, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = DiarioLectorForm(request.POST, instance=entrada, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada actualizada correctamente.')
            return redirect('diario_lector')
    else:
        form = DiarioLectorForm(instance=entrada, usuario=request.user)

    return render(request, 'biblioteca/editar_entrada.html', {
        'form': form,
        'entrada': entrada,
    })


# ------------------------
# ELIMINAR ENTRADA DIARIO
# ------------------------
@login_required
def eliminar_entrada(request, pk):
    entrada = get_object_or_404(DiarioLector, pk=pk, usuario=request.user)

    if request.method == 'POST':
        entrada.delete()
        messages.success(request, 'Entrada eliminada del diario.')
        return redirect('diario_lector')

    return render(request, 'biblioteca/eliminar_entrada.html', {'entrada': entrada})


# ------------------------
# RECOMENDACIONES PERSONALIZADAS
# ------------------------
@login_required
def recomendaciones(request):
    """
    Muestra recomendaciones basadas en los libros del usuario
    con estado: iniciado, en_curso, finalizado.
    Usa el modelo KNN cargado en recomendaciones.py
    """

    # Historial que define gustos del usuario
    libros_base = LibroLeido.objects.filter(
        usuario=request.user,
        estado__in=['iniciado', 'en_curso', 'finalizado']
    ).exclude(isbn__isnull=True).exclude(isbn__exact='')

    isbns_usuario = [l.isbn for l in libros_base]

    recomendaciones = recomendar_para_usuario(isbns_usuario, top_n=15)

    # Libros ya marcados como pendientes
    pendientes_isbns = set(
        Pendiente.objects.filter(usuario=request.user)
        .values_list('isbn', flat=True)
    )

    for r in recomendaciones:
        r['is_pending'] = r['isbn'] in pendientes_isbns

    return render(request, 'biblioteca/recomendaciones.html', {
        'recomendaciones': recomendaciones,
        'tiene_base': bool(isbns_usuario),
    })


# ------------------------
# MARCAR LIBRO COMO PENDIENTE (desde recomendaciones)
# ------------------------
from django.views.decorators.http import require_POST

@require_POST
@login_required
def marcar_pendiente(request):
    isbn = request.POST.get('isbn')
    titulo = request.POST.get('titulo')
    autor = request.POST.get('autor', '')

    if not titulo:
        # Si viene por AJAX y falta info
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Falta título'}, status=400)
        messages.error(request, 'No se pudo agregar el libro a pendientes.')
        return HttpResponseRedirect(reverse('recomendaciones'))

    pendiente, creado = Pendiente.objects.get_or_create(
        usuario=request.user,
        isbn=isbn if isbn else None,
        titulo=titulo,
        defaults={'autor': autor}
    )

    if creado:
        messages.success(request, f'"{titulo}" fue agregado a tu lista de Pendientes. ✨')
    else:
        messages.info(request, f'"{titulo}" ya estaba en tu lista de Pendientes.')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})

    return HttpResponseRedirect(reverse('recomendaciones'))


# ------------------------
# ESTADÍSTICAS
# ------------------------
@login_required
def estadisticas(request):
    usuario = request.user

    # Distribución por estado
    resumen = (LibroLeido.objects
               .filter(usuario=usuario)
               .values('estado')
               .annotate(total=Count('estado')))

    etiquetas = [item['estado'] for item in resumen]
    cantidades = [item['total'] for item in resumen]

    # Evolución mensual
    libros = LibroLeido.objects.filter(usuario=usuario, fecha_inicio__isnull=False)

    meses_set = set()
    estado_mensual = defaultdict(lambda: defaultdict(int))

    for libro in libros:
        estado = libro.estado
        inicio = libro.fecha_inicio
        fin = libro.fecha_fin if libro.fecha_fin else date.today()

        if estado in ['iniciado', 'en_curso']:
            mes_actual = inicio.replace(day=1)
            while mes_actual <= fin:
                mes_str = mes_actual.strftime('%b %Y')
                estado_mensual[estado][mes_str] += 1
                meses_set.add(mes_str)
                mes_actual += relativedelta(months=1)

        elif estado == 'finalizado':
            mes_str = inicio.strftime('%b %Y')
            estado_mensual[estado][mes_str] += 1
            meses_set.add(mes_str)

    meses_ordenados = sorted(
        meses_set,
        key=lambda m: datetime.strptime(m, '%b %Y')
    )

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

# ------------------------
# LISTA DE PENDIENTES   
# ------------------------
@login_required
def pendientes(request):
    """
    Muestra la lista de libros que el usuario marcó como pendientes.
    """
    lista = Pendiente.objects.filter(usuario=request.user).order_by('-creado')

    return render(request, 'biblioteca/pendientes.html', {
        'pendientes': lista,
    })

# ------------------------
# CONVERTIR PENDIENTE A LIBRO LEÍDO 
# ------------------------
@login_required
@require_POST
def pendiente_a_biblioteca(request, pendiente_id):
    """
    Convierte un libro Pendiente en un LibroLeido en la biblioteca del usuario.
    """
    pendiente = get_object_or_404(Pendiente, id=pendiente_id, usuario=request.user)

    # Verificar si ya existe en la biblioteca del usuario
    libro_existente = None

    if pendiente.isbn:
        libro_existente = LibroLeido.objects.filter(
            usuario=request.user,
            isbn=pendiente.isbn
        ).first()

    if not libro_existente:
        libro_existente = LibroLeido.objects.filter(
            usuario=request.user,
            titulo__iexact=pendiente.titulo
        ).first()

    if libro_existente:
        messages.info(request, f'"{pendiente.titulo}" ya está en tu biblioteca.')
    else:
        libro = LibroLeido.objects.create(
            usuario=request.user,
            titulo=pendiente.titulo,
            autor=pendiente.autor or "Desconocido",
            isbn=pendiente.isbn,
            estado='pendiente',  # empieza como pendiente en la biblioteca
        )
        messages.success(request, f'"{libro.titulo}" fue agregado a tu biblioteca. ✨')

    # Opcional: eliminarlo de la lista de Pendientes una vez movido
    pendiente.delete()

    return redirect('biblioteca')
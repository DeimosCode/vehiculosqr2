import os
import io
import base64
import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from .models import Vehiculo, ObservacionVehiculo, ImagenObservacion


def registrar_vehiculo(request):
    if request.method == "POST":
        codigo = request.POST.get('codigo')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        anio = request.POST.get('anio')

        # Validar que los campos no estén vacíos
        if not codigo or not marca or not modelo or not anio:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'vehiculos/registrar_vehiculo.html', {'MEDIA_URL': settings.MEDIA_URL})

        # Crear y guardar el objeto Vehiculo
        vehiculo = Vehiculo(codigo=codigo, marca=marca, modelo=modelo, anio=anio)
        vehiculo.save()

        messages.success(request, 'Vehículo registrado exitosamente.')
        return redirect('home')

    return render(request, 'vehiculos/registrar_vehiculo.html', {'MEDIA_URL': settings.MEDIA_URL})


def consultar_vehiculo(request):
    codigo_qr = None
    vehiculo = None
    codigo = None

    if request.method == "POST":
        codigo = request.POST.get('codigo')
    else:
        codigo = request.GET.get('codigo')

    if codigo:
        try:
            vehiculo = Vehiculo.objects.get(codigo=codigo)

            # Generar el código QR en memoria
            qr_image = qrcode.make(codigo)
            buffered = io.BytesIO()
            qr_image.save(buffered, format="PNG")
            qr_image_str = base64.b64encode(buffered.getvalue()).decode()
            codigo_qr = f"data:image/png;base64,{qr_image_str}"

            messages.success(request, 'Vehículo encontrado exitosamente.')
        except Vehiculo.DoesNotExist:
            messages.error(request, 'Vehículo no encontrado.')

    return render(request, 'vehiculos/consultar.html', {
        'vehiculo': vehiculo,
        'codigo_qr': codigo_qr,
        'MEDIA_URL': settings.MEDIA_URL
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Has iniciado sesión exitosamente.')
            return redirect('home')
        else:
            messages.error(request, 'Credenciales incorrectas.')

    return render(request, 'vehiculos/login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        confirm_password = request.POST.get('confirm_password')

        # Validar que los campos no estén vacíos
        if not username or not password or not email or not confirm_password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'vehiculos/register.html')

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'vehiculos/register.html')

        # Crear un nuevo usuario
        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe. Elige otro.')
                return render(request, 'vehiculos/register.html')

            User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, 'Usuario registrado exitosamente. Puedes iniciar sesión ahora.')
            return redirect('login')
        except Exception:
            messages.error(request, 'Error al registrar el usuario. Asegúrate de que el nombre de usuario no exista.')

    return render(request, 'vehiculos/register.html')


def home_view(request):
    return render(request, 'vehiculos/home.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


def registrar_observacion(request, codigo):
    if request.method == "POST":
        vehiculo = get_object_or_404(Vehiculo, codigo=codigo)
        descripcion = request.POST.get('descripcion')
        creado_por = request.user.username if request.user.is_authenticated else "Sistema"

        observacion = ObservacionVehiculo.objects.create(
            vehiculo=vehiculo,
            descripcion=descripcion,
            creado_por=creado_por
        )

        # Imagen de la cámara (opcional)
        foto_base64 = request.POST.get('fotoBase64')
        if foto_base64:
            observacion.save_image_from_base64(foto_base64)
            observacion.save()

            # También como imagen adicional
            ImagenObservacion.objects.create(
                observacion=observacion,
                imagen_base64=foto_base64
            )

        # Imágenes subidas localmente (pueden ser varias)
        for f in request.FILES.getlist('imagenes_base64'):
            img_data = base64.b64encode(f.read()).decode()
            ImagenObservacion.objects.create(
                observacion=observacion,
                imagen_base64=img_data
            )

        messages.success(request, 'Observación guardada correctamente.')
        return redirect(f"{reverse('consulta_vehiculo')}?codigo={codigo}")

    messages.error(request, 'Método no permitido.')
    return redirect(f"{reverse('consulta_vehiculo')}?codigo={codigo}")


def detalle_vehiculo(request, codigo):
    vehiculo = get_object_or_404(Vehiculo, codigo=codigo)
    observaciones = vehiculo.observaciones.all().order_by('-fecha')

    return render(request, 'vehiculos/detalle_vehiculo.html', {
        'vehiculo': vehiculo,
        'observaciones': observaciones,
    })


# --- Manejo de errores personalizados --- #

def error_400_view(request, exception):
    return render(request, "400.html", status=400)

def error_404_view(request, exception):
    return render(request, "404.html", status=404)

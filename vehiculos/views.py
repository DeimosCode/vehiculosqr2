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
from datetime import datetime
from .models import Vehiculo, ObservacionVehiculo, ImagenObservacion


def registrar_vehiculo(request):
    if request.method == "POST":
        codigo = request.POST.get('codigo')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')
        anio = request.POST.get('anio')  # Este puede ser None/empty
        
        # Validar solo los campos obligatorios
        if not codigo or not marca or not modelo:
            messages.error(request, 'Los campos código, marca y modelo son obligatorios.')
            return render(request, 'vehiculos/registrar_vehiculo.html', {'MEDIA_URL': settings.MEDIA_URL})

        # Convertir año a entero si tiene valor, sino guardar como None
        try:
            anio = int(anio) if anio else None
        except ValueError:
            messages.error(request, 'El año debe ser un número válido.')
            return render(request, 'vehiculos/registrar_vehiculo.html', {'MEDIA_URL': settings.MEDIA_URL})

        # Validación adicional opcional para el año
        if anio is not None:
            current_year = datetime.now().year
            if anio < 1900 or anio > current_year + 1:
                messages.error(request, f'El año debe estar entre 1900 y {current_year + 1}')
                return render(request, 'vehiculos/registrar_vehiculo.html', {'MEDIA_URL': settings.MEDIA_URL})

        # Crear y guardar el objeto Vehiculo (anio puede ser None)
        vehiculo = Vehiculo(codigo=codigo, marca=marca, modelo=modelo, anio=anio)
        vehiculo.save()

        messages.success(request, 'Vehículo registrado exitosamente.')
        return redirect('home')

    return render(request, 'vehiculos/registrar_vehiculo.html', {
        'MEDIA_URL': settings.MEDIA_URL,
        'current_year': datetime.now().year  # Para usar en el template
    })


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
    vehiculos = Vehiculo.objects.all().order_by('-fecha_registro')  # o por '-id'
    return render(request, 'vehiculos/home.html', {'vehiculos': vehiculos})



def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


def registrar_observacion(request, codigo_vehiculo):
    if request.method == "POST":
        vehiculo = get_object_or_404(Vehiculo, codigo=codigo_vehiculo)
        descripcion = request.POST.get('descripcion')
        creado_por = request.user.username if request.user.is_authenticated else "Sistema"

        # Validar que haya al menos una imagen (cámara o subida)
        foto_base64 = request.POST.get('fotoBase64')
        imagenes_subidas = request.FILES.getlist('imagenes[]')
        
        if not foto_base64 and not imagenes_subidas:
            messages.error(request, 'Debe agregar al menos una imagen.')
            return redirect(f"{reverse('consulta_vehiculo')}?codigo={codigo_vehiculo}")

        # Crear la observación
        observacion = ObservacionVehiculo.objects.create(
            vehiculo=vehiculo,
            descripcion=descripcion,
            creado_por=creado_por
        )

        # Guardar imagen de la cámara si existe
        if foto_base64:
            # Limpiar el data URL si viene con prefijo
            if 'base64,' in foto_base64:
                foto_base64 = foto_base64.split('base64,')[1]
                
            ImagenObservacion.objects.create(
                observacion=observacion,
                imagen_base64=foto_base64
            )

        # Guardar imágenes subidas
        for imagen in imagenes_subidas:
            try:
                img_data = base64.b64encode(imagen.read()).decode('utf-8')
                ImagenObservacion.objects.create(
                    observacion=observacion,
                    imagen_base64=img_data
                )
            except Exception as e:
                print(f"Error al procesar imagen: {e}")
                continue

        messages.success(request, 'Observación guardada correctamente.')
        return redirect(f"{reverse('consulta_vehiculo')}?codigo={codigo_vehiculo}")

    return redirect('home')


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

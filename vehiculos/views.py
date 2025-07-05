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
    codigo = request.POST.get('codigo') or request.GET.get('codigo')

    if codigo:
        try:
            vehiculo = Vehiculo.objects.get(codigo=codigo)

            # Generar el código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(codigo)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            codigo_qr = base64.b64encode(buffered.getvalue()).decode()

            messages.success(request, 'Vehículo encontrado exitosamente.')
        except Vehiculo.DoesNotExist:
            messages.error(request, f'Vehículo con código {codigo} no encontrado.')
            codigo = None  # Limpiar el código si no existe

    return render(request, 'vehiculos/consultar.html', {
        'vehiculo': vehiculo,
        'codigo_qr': f"data:image/png;base64,{codigo_qr}" if codigo_qr else None,
        'codigo_actual': codigo,  # Pasar el código actual a la plantilla
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

import json

# vehiculos/views.py

def registrar_observacion(request, codigo_vehiculo):
    if request.method == 'POST':
        try:
            vehiculo = get_object_or_404(Vehiculo, codigo=codigo_vehiculo)
            
            descripcion = request.POST.get('descripcion', '').strip()
            imagen_base64 = request.POST.get('fotoBase64', '')
            imagenes_base64 = request.POST.get('imagenes_base64', '[]')
            
            # Validación de la descripción
            if len(descripcion) < 1:
                messages.error(request, 'La descripción debe tener al menos 10 caracteres')
                return redirect(f"{reverse('consulta_vehiculo')}?codigo={codigo_vehiculo}")
            
            # Crear la observación
            observacion = ObservacionVehiculo(
                vehiculo=vehiculo,
                descripcion=descripcion,
                creado_por=request.user.username if request.user.is_authenticated else 'Anónimo'
            )
            
            # Procesar imagen principal si existe
            if imagen_base64 and imagen_base64.startswith('data:image'):
                observacion.imagen_base64 = imagen_base64.split(',')[1]
            
            # Procesar imágenes adicionales si existen
            try:
                imagenes = json.loads(imagenes_base64)
                if imagenes and isinstance(imagenes, list):
                    observacion.imagenes_base64 = json.dumps(imagenes)
            except json.JSONDecodeError:
                pass
            
            observacion.save()
            
            messages.success(request, 'Observación registrada correctamente')
            # Redirige usando el nombre correcto de la URL
            return redirect(f"{reverse('consulta_vehiculo')}?codigo={codigo_vehiculo}")
            
        except Vehiculo.DoesNotExist:
            messages.error(request, 'Vehículo no encontrado')
            return redirect('consulta_vehiculo')  # Usa el mismo nombre aquí
        except Exception as e:
            messages.error(request, f'Error al registrar observación: {str(e)}')
            return redirect('consulta_vehiculo')  # Y aquí
    
    return redirect('consulta_vehiculo')  # Y a


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

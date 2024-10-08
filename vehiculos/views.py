import os
import qrcode
import io
import base64
from django.shortcuts import render, redirect
from .models import Vehiculo
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages  # Importa para los mensajes

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
    if request.method == "POST":
        codigo = request.POST.get('codigo')
        try:
            vehiculo = Vehiculo.objects.get(codigo=codigo)

            # Generar el código QR en memoria
            qr_image = qrcode.make(codigo)
            buffered = io.BytesIO()
            qr_image.save(buffered, format="PNG")
            qr_image_str = base64.b64encode(buffered.getvalue()).decode()
            codigo_qr = f"data:image/png;base64,{qr_image_str}"

            # Mensaje de éxito al encontrar el vehículo
            messages.success(request, 'Vehículo encontrado exitosamente.')

            return render(request, 'vehiculos/consultar.html', {
                'vehiculo': vehiculo,
                'codigo_qr': codigo_qr,
                'MEDIA_URL': settings.MEDIA_URL
            })
        except Vehiculo.DoesNotExist:
            messages.error(request, 'Vehículo no encontrado.')
            return render(request, 'vehiculos/consultar.html', {'MEDIA_URL': settings.MEDIA_URL})

    return render(request, 'vehiculos/consultar.html', {'MEDIA_URL': settings.MEDIA_URL})

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

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')  # Captura el correo electrónico
        confirm_password = request.POST.get('confirm_password')  # Captura la confirmación de contraseña

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
            # Verificar si el nombre de usuario ya existe
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe. Elige otro.')
                return render(request, 'vehiculos/register.html')

            # Crear el usuario
            User.objects.create_user(username=username, password=password, email=email)
            messages.success(request, 'Usuario registrado exitosamente. Puedes iniciar sesión ahora.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Error al registrar el usuario. Asegúrate de que el nombre de usuario no exista.')

    return render(request, 'vehiculos/register.html')


def home_view(request):
    return render(request, 'vehiculos/home.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

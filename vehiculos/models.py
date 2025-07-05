from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone
import json
from django.core.exceptions import ValidationError

from django.db import models
from django.utils import timezone
import json
from django.core.exceptions import ValidationError

class Vehiculo(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField()

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio})"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ['marca', 'modelo']

class ObservacionVehiculo(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo, 
        on_delete=models.CASCADE,
        related_name='observaciones',
        verbose_name='Vehículo asociado'
    )
    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de observación'
    )
    descripcion = models.TextField(
        verbose_name='Descripción de la observación'
    )
    imagen_base64 = models.TextField(
        blank=True,
        null=True,
        verbose_name='Imagen en Base64'
    )
    imagenes_base64 = models.TextField(
        blank=True,
        null=True,
        verbose_name='Imágenes adicionales en Base64 (JSON)'
    )
    creado_por = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Usuario que creó la observación'
    )

    class Meta:
        verbose_name = 'Observación de vehículo'
        verbose_name_plural = 'Observaciones de vehículos'
        ordering = ['-fecha']

    def __str__(self):
        return f"Obs. {self.id} - {self.vehiculo} ({self.fecha.strftime('%d/%m/%Y')})"

    def clean(self):
        """Validación opcional para imágenes"""
        pass  # Eliminamos la validación obligatoria de imágenes

    def get_imagen_data(self):
        """Devuelve la imagen principal como data URI"""
        if self.imagen_base64:
            return f"data:image/jpeg;base64,{self.imagen_base64}"
        return None

    def get_imagenes_base64(self):
        """Devuelve una lista de imágenes adicionales en base64"""
        if self.imagenes_base64:
            try:
                return json.loads(self.imagenes_base64)
            except json.JSONDecodeError:
                return []
        return []

    def add_imagen(self, base64_string):
        """Añade una imagen a la lista de imágenes adicionales"""
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        imagenes = self.get_imagenes_base64()
        imagenes.append(base64_string)
        self.imagenes_base64 = json.dumps(imagenes)
        self.save()

    def save(self, *args, **kwargs):
        """Validación antes de guardar"""
        self.clean()
        super().save(*args, **kwargs)

class ImagenObservacion(models.Model):
    observacion = models.ForeignKey(
        ObservacionVehiculo,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name='Observación asociada'
    )
    imagen_base64 = models.TextField(
        verbose_name='Imagen en Base64'
    )
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Descripción de la imagen'
    )

    def get_image_data(self):
        if self.imagen_base64:
            return f"data:image/jpeg;base64,{self.imagen_base64}"
        return None

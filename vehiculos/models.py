from django.db import models
from django.utils import timezone

class Vehiculo(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField()

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio})"

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

    def save_image_from_base64(self, base64_string):
        if base64_string.startswith('data:image'):
            header, base64_data = base64_string.split(';base64,')
            self.imagen_base64 = base64_data
        else:
            self.imagen_base64 = base64_string

    def get_image_data(self):
        if self.imagen_base64:
            return f"data:image/jpeg;base64,{self.imagen_base64}"
        return None

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

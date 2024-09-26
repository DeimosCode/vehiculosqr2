from django.db import models

class Vehiculo(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField()

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio})"
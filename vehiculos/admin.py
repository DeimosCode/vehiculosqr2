from django.contrib import admin
from .models import Vehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'marca', 'modelo', 'anio')  # Campos que deseas mostrar en la lista

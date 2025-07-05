from django.contrib import admin
from .models import Vehiculo, ObservacionVehiculo, ImagenObservacion

class ObservacionInline(admin.TabularInline):
    model = ObservacionVehiculo
    extra = 1
    readonly_fields = ('fecha',)
    fields = ('descripcion', 'imagen_base64', 'creado_por', 'fecha')
    show_change_link = True

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'marca', 'modelo', 'anio')
    search_fields = ('codigo', 'marca', 'modelo')
    list_filter = ('anio',)
    inlines = [ObservacionInline]


# Si deseas que ImagenObservacion aparezca como modelo en el panel admin:
@admin.register(ImagenObservacion)
class ImagenObservacionAdmin(admin.ModelAdmin):
    list_display = ('observacion', 'descripcion')
    search_fields = ('descripcion', 'observacion__vehiculo__codigo')

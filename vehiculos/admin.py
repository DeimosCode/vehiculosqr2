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


from django.contrib import admin
from django.db import connection
from django.urls import path
from django.http import HttpResponse
from django.template.response import TemplateResponse
import os

class CustomAdminSite(admin.AdminSite):
    site_header = "Panel de Administración de Vehículos"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("db-size/", self.admin_view(self.db_size_view))
        ]
        return custom_urls + urls

    def db_size_view(self, request):
        db_size = self.get_db_size()
        context = dict(
            self.each_context(request),
            title='Tamaño de la Base de Datos',
            db_size=db_size
        )
        return TemplateResponse(request, "admin/db_size.html", context)

    def get_db_size(self):
        engine = connection.settings_dict['ENGINE']
        if 'postgresql' in engine:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
                return cursor.fetchone()[0]
        elif 'sqlite3' in engine:
            db_path = connection.settings_dict['NAME']
            size_bytes = os.path.getsize(db_path)
            return self.size_format(size_bytes)
        else:
            return "Motor de base de datos no soportado"

    def size_format(self, size):
        # Formato bonito para el tamaño en bytes
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

# Usar este admin personalizado
admin_site = CustomAdminSite(name='custom_admin')
admin_site.register(Vehiculo, VehiculoAdmin)
admin_site.register(ImagenObservacion, ImagenObservacionAdmin)

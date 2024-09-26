from django.urls import path
from .views import registrar_vehiculo, consultar_vehiculo, login_view, register_view, home_view, logout_view
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('registrar/', login_required(registrar_vehiculo), name='registrar_vehiculo'),
    path('consultar/', login_required(consultar_vehiculo), name='consulta_vehiculo'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('home/', login_required(home_view), name='home'),
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

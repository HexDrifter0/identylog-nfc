# urls.py - Todas las rutas del sitio
from django.contrib import admin
from django.urls import path
from nfc_manager import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_inicio, name='landing_inicio'),
    path('t/<str:token>/', views.landing_publica, name='landing_publica'),
    path('activar/<str:token>/', views.activar_soporte, name='activar_soporte'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('editar/<int:momento_id>/', views.editar_momento, name='editar_momento'),
]
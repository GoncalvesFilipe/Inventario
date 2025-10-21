from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    # ADMINISTRATIVO PADRÃO DO DJANGO
    path('admin/', admin.site.urls),
    # PÁGINA INICIAL
    path('', views.index, name='index'),
    #path('inventarios', views.inventarios, name='inventarios')
]

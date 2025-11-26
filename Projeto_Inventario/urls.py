from django.contrib import admin
from django.urls import path, include
from app import views as app_views
from users import views as users_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app_views.index, name='index'),

    # Login usando LoginView do Django e template da app users
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),

    # Register e logout da app users
    path('register/', users_views.register_view, name='register'),
    path('logout/', users_views.logout_view, name='logout'),
    
    path('painel/', include('app.urls_admin')),
]


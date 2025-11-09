
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import FormularioLoginUsuario

urlpatterns = [
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/F_Tela_Login.html',  
        authentication_form=FormularioLoginUsuario
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('chefe/', views.historia_chefe, name = "historia_chefe")
]
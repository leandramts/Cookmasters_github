
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import FormularioLoginUsuario

app_name = 'usuarios'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='usuarios/F_Tela_Login.html',  
        authentication_form=FormularioLoginUsuario
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('chefe/', views.historia_chefe, name = "historia_chefe"),
    path('cadastro/', views.escolher_tipo_usuario, name='escolher_tipo'),
    path('cadastro/chefe/', views.cadastro_chefe, name='cadastro_chefe'),
    path('cadastro/consumidor/', views.cadastro_consumidor, name='cadastro_consumidor'),
    path('cadastro/adm/', views.cadastro_adm, name='cadastro_adm'),
]

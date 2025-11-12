# cookmasters_app/urls.py
from django.urls import path
from . import views # Importa o seu views.py gigante

urlpatterns = [
    # Rotas da Home
    path('', views.home_view, name='home'),

    # Rotas de Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Rotas de Cadastro
    path('cadastro/', views.escolher_tipo_usuario, name='escolher_tipo'),
    path('cadastro/chefe/', views.cadastro_chefe, name='cadastro_chefe'),
    path('cadastro/consumidor/', views.cadastro_consumidor, name='cadastro_consumidor'),
    path('cadastro/adm/', views.cadastro_adm, name='cadastro_adm'),
    path('chefe/historia/', views.historia_chefe, name='historia_chefe'),

    # Rotas de Receitas
    path('receitas/cadastrar/', views.cadastrar_receita, name='cadastrar_receita'),
    path('receitas/ingredientes/', views.cadastrar_ingredientes, name='cadastrar_ingredientes'),
]
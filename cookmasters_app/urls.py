# cookmasters_app/urls.py
from django.urls import path
from . import views # Importa o seu views.py gigante

urlpatterns = [
    # Rotas da Home
    path('', views.home_view, name='home'),
    path('filtro/', views.filtro, name='filtro'),


    # Rotas de Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Rotas de Cadastro
    path('cadastro/', views.escolher_tipo_usuario, name='escolher_tipo'),
    path('cadastro/chefe/', views.cadastro_chefe, name='cadastro_chefe'),
    path('cadastro/consumidor/', views.cadastro_consumidor, name='cadastro_consumidor'),

    # Rotas de Receitas
    path('receitas/cadastrar/', views.cadastrar_receita, name='cadastrar_receita'),
    path('receitas/visualizar/<int:receita_id>/', views.visualizar_receita, name='visualizar_receita'),
    path("receita/<int:receita_id>/comprar/", views.comprar_receita, name="comprar_receita"),
    path('receitas/<int:receita_id>/pagamento/', views.selecionar_pagamento, name='selecionar_pagamento'),
    path("receitas/<int:receita_id>/avaliar/", views.avaliar_receita, name="avaliar_receita"),


    #Rotas de Visualizacao
    path("chefe/<int:id>/", views.visualizar_chefe, name="visualizar_chefe"),
    path("cozinhe-me/", views.cozinhe_me, name='cozinheme')
]
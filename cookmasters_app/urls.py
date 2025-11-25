# cookmasters_app/urls.py
from django.urls import path
from . import views 

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
    path('receita/editar/<int:receita_id>/', views.editar_receita, name='editar_receita'),
    path('receita/excluir/<int:receita_id>/', views.chefe_excluir_receita, name='excluir_receita'),


    #Rotas de Visualizacao
    path("chefe/<int:id>/", views.visualizar_chefe, name="visualizar_chefe"),
    path("cozinhe-me/", views.cozinhe_me, name='cozinheme'),
    path('relatorio/vendas/', views.relatorio_vendas_chefe, name='relatorio_vendas_chefe'),
    path("receitas/minhas/", views.minhas_receitas, name="minhas_receitas"),


    #Rotas do Carrinho de compras
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path("carrinho/adicionar/<int:receita_id>/", views.adicionar_ao_carrinho, name="adicionar_ao_carrinho"),
    path("carrinho/remover/<int:receita_id>/", views.remover_do_carrinho, name="remover_do_carrinho"),
    path("carrinho/pagar/", views.pagamento_carrinho, name="pagamento_carrinho"),

           path("adm/usuarios/", views.listar_usuarios, name="listar_usuarios"),
    path("adm/usuarios/bloquear/<int:user_id>/", views.bloquear_usuario, name="bloquear_usuario"),
    path("adm/usuarios/desbloquear/<int:user_id>/", views.desbloquear_usuario, name="desbloquear_usuario"),

    # Receitas
    path("adm/receitas/", views.listar_receitas, name="listar_receitas"),
    path("adm/receitas/excluir/<int:receita_id>/", views.adm_excluir_receita, name="adm_excluir_receita"),

    # Comentários
    path("adm/comentarios/", views.listar_comentarios, name="listar_comentarios"),
    path("adm/comentarios/excluir/<int:comentario_id>/", views.excluir_comentario, name="excluir_comentario"),

]
from django.urls import path
from . import views

app_name = 'receitas'

urlpatterns = [
    path('ingredientes/', views.cadastrar_ingredientes, name='cadastrar_ingredientes'),
    path('cadastrar/', views.cadastrar_receita, name='cadastrar_receita')
]
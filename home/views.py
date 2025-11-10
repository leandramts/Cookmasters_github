
from django.shortcuts import render
from receitas.models import E_Receita 

def home_view(request):
    receitas_em_destaque = E_Receita.objects.all()
    
    contexto = {
        'receitas': receitas_em_destaque
    }
    
    return render(request, 'home/home.html', contexto)
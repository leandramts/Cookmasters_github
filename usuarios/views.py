from django.shortcuts import render, redirect
from .forms import FormularioCadastroUsuario

def cadastro_view(request):
    if request.method == 'POST':
        form = FormularioCadastroUsuario(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('home')
    else:
        form = FormularioCadastroUsuario()
    
    return render(request, 'usuarios/F_Tela_Cadastro.html', {'form': form})


def historia_chefe(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        resumo = request.POST.get('resumo')
        receitas = request.POST.get('receitas').split(';')  # separa receitas por ;
        contexto = {
            'nome': nome,
            'resumo': resumo,
            'receitas': receitas
        }
        return render(request, 'usuarios/chefe_historia.html', contexto)
    else:
        form = HistoriaChefe()
    return render(request, 'usuarios/chefe_form.html')

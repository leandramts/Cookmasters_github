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
    return render(request, 'usuarios/chefe_historia.html')
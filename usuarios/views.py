from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormularioCadastroUsuario, HistoriaChefeForm


def escolher_tipo_usuario(request):
    return render(request, 'usuarios/F_Tela_Escolher_Tipo.html')

def cadastro_chefe(request):
    if request.method == 'POST':
        form = FormularioCadastroUsuario(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.tipo = 'chefe'  
            usuario.save()
            messages.success(request, f'Chefe {usuario.nome} cadastrado com sucesso!')
            return redirect('historia_chefe')
    else:
        form = FormularioCadastroUsuario()

    return render(request, 'usuarios/F_Tela_Cadastro_Chefe.html', {'form': form})

def cadastro_consumidor(request):
    if request.method == 'POST':
        form = FormularioCadastroUsuario(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.tipo = 'consumidor'
            usuario.save()
            messages.success(request, f'Consumidor {usuario.nome} cadastrado com sucesso!')
            return redirect('home')
    else:
        form = FormularioCadastroUsuario()

    return render(request, 'usuarios/F_Tela_Cadastro_Consumidor.html', {'form': form})

# Cadastro de administrador (acesso restrito)
def cadastro_adm(request):
    if request.method == 'POST':
        email = request.POST.get('email')
      
        messages.info(request, f'Solicitação de acesso enviada para o administrador da empresa ({email}).')
        return redirect('home')

    return render(request, 'usuarios/F_Tela_Cadastro_Adm.html')

def historia_chefe(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        resumo = request.POST.get('resumo')
        receitas = request.POST.get('receitas').split(';')  
        contexto = {
            'nome': nome,
            'resumo': resumo,
            'receitas': receitas
        }
        return render(request, 'usuarios/chefe_historia.html', contexto)
    else:
        form = HistoriaChefeForm()
        return render(request, 'usuarios/F_Tela_Historia_Chefe.html', {'form': form})

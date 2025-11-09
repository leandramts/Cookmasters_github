
from django.shortcuts import render, redirect
from .forms import ReceitaForm, IngredienteForm
from .models import E_Ingrediente, E_Receita

def cadastrar_ingredientes(request):
    if request.method == 'POST':
        form = IngredienteForm(request.POST)
        if form.is_valid():
            ingrediente = form.save()
            # guarda o ID do ingrediente recém criado na sessão
            if 'ingredientes_ids' not in request.session:
                request.session['ingredientes_ids'] = []
            request.session['ingredientes_ids'].append(ingrediente.id)
            request.session.modified = True

            # redireciona para adicionar mais ingredientes ou ir para receita
            if 'finalizar' in request.POST:
                return redirect('cadastrar_receita')
            else:
                return redirect('cadastrar_ingredientes')
    else:
        form = IngredienteForm()

    return render(request, 'ingredientes_form.html', {'form': form})


def cadastrar_receita(request):
    ingredientes_ids = request.session.get('ingredientes_ids', [])
    ingredientes = E_Ingrediente.objects.filter(id__in=ingredientes_ids)

    if request.method == 'POST':
        form = ReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.save()
            receita.ingredientes.set(ingredientes)
            receita.save()

            # limpa a sessão depois de salvar
            if 'ingredientes_ids' in request.session:
                del request.session['ingredientes_ids']

            return redirect('sucesso')
    else:
        form = ReceitaForm()

    return render(request, 'receita_form.html', {
        'form': form,
        'ingredientes': ingredientes
    })

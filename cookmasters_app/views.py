
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import E_UsuarioGeral, E_Chefe, E_Consumidor, E_Receita, E_Ingrediente, E_Tag
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count,Q


def home_view(request):
    receitas_em_destaque = E_Receita.objects.order_by('-nota')[:6]
    contexto = {
        'receitas': receitas_em_destaque
    }
    return render(request, 'home.html', contexto)


def login_view(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('password')

        if not email or not senha:
            messages.error(request, "Por favor, preencha o e-mail e a senha.")
            return render(request, 'F_Tela_Login.html')

        user = authenticate(request, username=email, password=senha)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "E-mail ou senha inválidos.")
            return render(request, 'F_Tela_Login.html')
    else:
        return render(request, 'F_Tela_Login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')



def escolher_tipo_usuario(request):

    return render(request, 'F_Tela_Escolher_Tipo.html')

def cadastro_consumidor(request):

    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')
        
        if not nome or not email or not senha or not senha_confirm:
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

        if senha != senha_confirm:
            messages.error(request, "As senhas não são iguais.")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

        if E_UsuarioGeral.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

        try:
            user = E_UsuarioGeral.objects.create_user(
                email=email,
                nome=nome,
                password=senha
            )

            E_Consumidor.objects.create(usuario=user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Consumidor {nome} cadastrado com sucesso!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao criar sua conta: {e}")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

    else:
        return render(request, 'F_Tela_Cadastro_Consumidor.html')

def cadastro_chefe(request):

    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')
        cpf = request.POST.get('cpf')
        descricao = request.POST.get('descricao')

        if not nome or not email or not senha or not senha_confirm or not cpf or not descricao:
             messages.error(request, "Todos os campos são obrigatórios.")
             return render(request, 'F_Tela_Cadastro_Chefe.html')

        if senha != senha_confirm:
            messages.error(request, "As senhas não são iguais.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')
        
        if E_UsuarioGeral.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')


        try:
            with transaction.atomic():

                user = E_UsuarioGeral.objects.create_user(
                    email=email,
                    nome=nome,
                    password=senha
                )

                E_Chefe.objects.create(
                    usuario=user,
                    cpf=cpf,
                    descricao = descricao
                )

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Chefe {nome} cadastrado com sucesso!')
            return redirect('home')

        except Exception as e:
                messages.error(request, f"Ocorreu um erro: {e}")
                return render(request, 'F_Tela_Cadastro_Chefe.html')

        # GET
    return render(request, 'F_Tela_Cadastro_Chefe.html')


def visualizar_chefe(request, id):
    chefe = get_object_or_404(E_Chefe, id=id)
    receitas = E_Receita.objects.filter(autor=chefe)

    return render(request, "F_Tela_Visualizar_Chefe.html", {"chefe":chefe, "receitas": receitas})


 

@login_required
def cadastrar_receita(request):
    if request.method == 'POST':
        try:
            autor = E_Chefe.objects.get(usuario=request.user)
            nome = request.POST.get('nome')
            descricao = request.POST.get('descricao')
            preco = request.POST.get('preco')
            modo_de_preparo = request.POST.get('modo_de_preparo')
            tags_selecionadas = request.POST.getlist('tags')
            ingredientes_texto = request.POST.get('ingredientes', '')

            # Criar receita
            receita = E_Receita.objects.create(
                autor=autor,
                nome=nome,
                descricao=descricao,
                preco=preco,
                modo_de_preparo=modo_de_preparo
            )

            # Adicionar tags
            for nome_tag in tags_selecionadas:
                tag, _ = E_Tag.objects.get_or_create(nome=nome_tag)
                receita.tags.add(tag)

            # Processar ingredientes
            ingredientes_lista = [i.strip() for i in ingredientes_texto.split(',') if i.strip()]
            for nome_ingrediente in ingredientes_lista:
                ingrediente, _ = E_Ingrediente.objects.get_or_create(nome=nome_ingrediente)
                receita.ingredientes.add(ingrediente)

            messages.success(request, 'Receita cadastrada com sucesso!')
            return redirect('home')

        except E_Chefe.DoesNotExist:
            messages.error(request, "Você precisa ser um Chefe para cadastrar receitas.")
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")

    # Passa as tags padrão para o HTML
    return render(request, 'F_Tela_Cadastro_Receita.html', {
        'tags': E_Receita.TAGS_PADRAO
    })

def cozinhe_me(request):
    # Lista completa de ingredientes, ordenados
    ingredientes = E_Ingrediente.objects.all().order_by("nome")

    # Ingredientes selecionados (vêm dos checkboxes)
    selecionados_ids = request.POST.getlist("ingredientes")
    ingredientes_selecionados = E_Ingrediente.objects.filter(id__in=selecionados_ids)

    receitas = []

    if ingredientes_selecionados:
        # Receitas que possuam pelo menos um ingrediente selecionado
        receitas_possiveis = (
            E_Receita.objects
            .filter(ingredientes__in=ingredientes_selecionados)
            .distinct()
        )

        # Mantém somente receitas que NÃO possuam ingredientes fora da seleção
        conjunto_selecionado = set(ingredientes_selecionados)

        receitas = [
            r for r in receitas_possiveis
            if set(r.ingredientes.all()).issubset(conjunto_selecionado)
        ]

    context = {
        "ingredientes": ingredientes,
        "ingredientes_selecionados": ingredientes_selecionados,
        "receitas": receitas,
    }

    return render(request, "F_Tela_CozinheMe.html", context)
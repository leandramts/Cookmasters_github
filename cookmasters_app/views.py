
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import E_UsuarioGeral, E_Chefe, E_Consumidor, E_Receita, E_Ingrediente, E_Tag, E_Compra, E_Pagamento, E_Avaliacoes
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count,Q
from decimal import Decimal
from django.db.models import Avg


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
        foto = request.FILES.get('foto')

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
                    descricao = descricao,
                    foto = foto
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
            tempo_preparo = request.POST.get('tempo_preparo')
            dificuldade = request.POST.get('dificuldade')
            foto = request.FILES.get('foto_receita')


            # Criar receita
            receita = E_Receita.objects.create(
                autor=autor,
                nome=nome,
                descricao=descricao,
                preco=preco,
                modo_de_preparo=modo_de_preparo,
                foto=foto,
                tempo_preparo = tempo_preparo,
                dificuldade = dificuldade

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

def visualizar_receita(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)

    modo_liberado = False
    avaliou = False

    consumidor = None

    if request.user.is_authenticated:
        consumidor = E_Consumidor.objects.filter(usuario=request.user).first()

        if consumidor:
            # Verifica se comprou
            modo_liberado = E_Compra.objects.filter(
                consumidor=consumidor,
                receita=receita
            ).exists()

            # Verifica se já avaliou
            avaliou = E_Avaliacoes.objects.filter(
                consumidor=consumidor,   # ✅ AGORA ESTÁ CORRETO
                receita=receita
            ).exists()

    contexto = {
        'receita': receita,
        'autor': receita.autor,
        'nome': receita.nome,
        'preco': receita.preco,
        'descricao': receita.descricao,
        'modo_de_preparo': receita.modo_de_preparo,
        'tempo_preparo': receita.tempo_preparo,
        'dificuldade': receita.get_dificuldade_display(),
        'nota': receita.nota,
        'tags': receita.tags.all(),
        'ingredientes': receita.ingredientes.all(),
        'foto': receita.foto.url if receita.foto else None,
        'modo_liberado': modo_liberado,
        'avaliou': avaliou,
    }

    return render(request, 'F_Tela_Visualizar_Receita.html', contexto)




@login_required
def comprar_receita(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)

    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem comprar receitas.")
        return redirect("visualizar_receita", receita_id=receita_id)

    if E_Compra.objects.filter(consumidor=consumidor, receita=receita).exists():
        messages.info(request, "Você já comprou esta receita.")
        return redirect("visualizar_receita", receita_id=receita_id)

    E_Compra.objects.create(consumidor=consumidor, receita=receita)

    messages.success(request, "Compra realizada! Modo de preparo liberado.")
    return redirect("visualizar_receita", receita_id=receita_id)




@login_required
def selecionar_pagamento(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)

    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem comprar.")
        return redirect("visualizar_receita", receita_id=receita_id)

    if request.method == "POST":
        metodo = request.POST.get("tipo_pagamento")

        if metodo not in ["pix", "credito", "debito"]:
            messages.error(request, "Método de pagamento inválido.")
            return redirect("selecionar_pagamento", receita_id=receita_id)

        taxa_adm = receita.preco * Decimal("0.10")

        pagamento = E_Pagamento.objects.create(
            consumidor=consumidor,
            tipo_pagamento=metodo,
            preco_total=receita.preco,
            taxa_adm=taxa_adm,
        )

        E_Compra.objects.create(
            consumidor=consumidor,
            receita=receita,
            pagamento=pagamento
        )

        messages.success(request, "Pagamento realizado com sucesso!")
        return redirect("visualizar_receita", receita_id=receita_id)

    return render(request, "F_Tela_Pagamento.html", {
        "receita": receita,
        "preco": receita.preco,
    })

@login_required
def avaliar_receita(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)

    # só consumidor pode avaliar
    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem avaliar receitas.")
        return redirect("visualizar_receita", receita_id=receita_id)

    # Só avalia se comprou
    if not E_Compra.objects.filter(consumidor=consumidor, receita=receita).exists():
        messages.error(request, "Você precisa comprar para avaliar esta receita.")
        return redirect("visualizar_receita", receita_id=receita_id)

    # POST = enviar avaliação
    if request.method == "POST":
        nota = int(request.POST.get("nota"))
        comentario = request.POST.get("comentario", "")

        # Impedir avaliação duplicada
        if E_Avaliacoes.objects.filter(consumidor=consumidor, receita=receita).exists():
            messages.error(request, "Você já avaliou esta receita.")
            return redirect("visualizar_receita", receita_id=receita_id)

        E_Avaliacoes.objects.create(
            receita=receita,
            consumidor=consumidor,
            nota=nota,
            comentario=comentario
        )

        # Atualizar nota média da receita
        from django.db.models import Avg
        media = E_Avaliacoes.objects.filter(receita=receita).aggregate(avg=Avg('nota'))['avg']
        receita.nota = media
        receita.save()

        messages.success(request, "Avaliação registrada com sucesso!")
        return redirect("visualizar_receita", receita_id=receita_id)

    # GET = mostrar formulário de avaliação
    return render(request, "F_Tela_Avaliar_Receita.html", {
        "receita": receita
    })


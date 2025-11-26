
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import E_UsuarioGeral, E_Chefe, E_Consumidor, E_Receita, E_Ingrediente, E_Tag, E_Compra, E_Pagamento, E_Avaliacoes
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count,Q, Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from django.db.models import Avg

# Home, nossa pagina inicial
def home_view(request):
    receitas_em_destaque = E_Receita.objects.order_by('-nota')
    todas_tags = E_Tag.objects.all()  

    return render(request, 'home.html', {
        'receitas': receitas_em_destaque,
        'todas_tags': todas_tags,
        'selecionada_dificuldade': "",
        'selecionado_tempo': "",
        'selecionadas_tags': [],
    })

#UC01 - Fazer Login
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

#UC00 - Cadastrar

def escolher_tipo_usuario(request):

    return render(request, 'F_Tela_Escolher_Tipo.html')

#UC00 - Cadastrar - quando for consumidor


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

#UC00 - Cadastrar - quando for Chefe
# UC00 - Cadastrar Chefe
def cadastro_chefe(request):

    if request.method == 'POST':

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')

        cpf = request.POST.get('cpf')
        descricao = request.POST.get('descricao')
        foto = request.FILES.get('foto')

        # Novos atributos bancários
        numero_agencia = request.POST.get('numero_agencia')
        nome_do_banco = request.POST.get('nome_do_banco')
        numero_conta = request.POST.get('numero_conta')

        # Validação dos campos obrigatórios
        if not nome or not email or not senha or not senha_confirm or not cpf or not descricao:
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')

        if senha != senha_confirm:
            messages.error(request, "As senhas não são iguais.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')

        if E_UsuarioGeral.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')

        if E_Chefe.objects.filter(cpf=cpf).exists():
            messages.error(request, "Já existe um chefe cadastrado com este CPF.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')

        try:
            with transaction.atomic():

                # Criação do usuário geral
                user = E_UsuarioGeral.objects.create_user(
                    email=email,
                    nome=nome,
                    password=senha
                )

                # Criação da entidade E_Chefe com os novos atributos
                E_Chefe.objects.create(
                    usuario=user,
                    cpf=cpf,
                    descricao=descricao,
                    foto=foto,
                    numero_agencia=numero_agencia,
                    nome_do_banco=nome_do_banco,
                    Numero_conta=numero_conta
                )

                # login automático após cadastro
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(request, f'Chefe {nome} cadastrado com sucesso!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")
            return render(request, 'F_Tela_Cadastro_Chefe.html')

    # GET
    return render(request, 'F_Tela_Cadastro_Chefe.html')


#UC03 - Visualizar Chefe

def visualizar_chefe(request, id):
    chefe = get_object_or_404(E_Chefe, id=id)
    receitas = E_Receita.objects.filter(autor=chefe)

    return render(request, "F_Tela_Visualizar_Chefe.html", {"chefe":chefe, "receitas": receitas})


 #UC15 - Publicar Receitas

@login_required
def cadastrar_receita(request):
    if request.method == 'POST':
        try:

            # Pegando os dados enviados pela F_Tela_Cadastro_Receita

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


            # Criar um objeto da classe E_Receita
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

            # Criando uma instância da classe E_ingrediente e relacionando-os com a receita
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




# UC04 - Selecionar Ingredientes

def cozinhe_me(request):

    # Lista completa de ingredientes, ordenados
    ingredientes = E_Ingrediente.objects.all().order_by("nome")

    # Ingredientes selecionados (vêm dos checkboxes) na tela de F_Tela_CozinheMe
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

        # Conjunto dos ingredientes selecionados
        conjunto_selecionado = set(ingredientes_selecionados)

        # Guarda as receitas cujo seu conjunto de ingredientes é subconjunto dos conjunto dos ingredientes selecionados 
        receitas = [
            r for r in receitas_possiveis
            if set(r.ingredientes.all()).issubset(conjunto_selecionado)
        ]

    # Guarda os ingredientes, os ingredientes selecionados e as receitas resultantes para mostrar na F_Tela_CozinheMe.html
    context = {
        "ingredientes": ingredientes,
        "ingredientes_selecionados": ingredientes_selecionados,
        "receitas": receitas,
    }

    return render(request, "F_Tela_CozinheMe.html", context)

# UC02 - Visualizar Receita

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
        'receita_id': receita.id,   # ✅ ADICIONAR ISTO
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


#UC05 - Comprar Receitas

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


#UC07 - Processar Pagamentos de Compras

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

#UC06 - Deixar avaliações

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

#UC09 - Acessar Receitas Por Filtro
def filtro(request):
    dificuldade = request.GET.get('dificuldade', '')
    tempo_preparo = request.GET.get('tempo', '')
    tags = request.GET.getlist('tags')

    receitas = E_Receita.objects.all()
    todas_tags = E_Tag.objects.all()
    if dificuldade:
        receitas = receitas.filter(dificuldade=dificuldade)
    
    match tempo_preparo:
        case "1":
            receitas = receitas.filter(tempo_preparo__lte=15)

        case "2":
            receitas = receitas.filter(tempo_preparo__gte=15, tempo_preparo__lte=30)

        case "3":
            receitas = receitas.filter(tempo_preparo__gte=30, tempo_preparo__lte=60)

        case "4":
            receitas = receitas.filter(tempo_preparo__gte=60)

        case _:
            pass  

    if tags:
        for tag_id in tags:
            receitas = receitas.filter(tags__id=tag_id)

    todas_tags = E_Tag.objects.all()

    return render (request, 'home.html', 
    {
        'receitas': receitas,
        'todas_tags': todas_tags,
        'selecionada_dificuldade': dificuldade,
        'selecionado_tempo': tempo_preparo,
        'selecionadas_tags': tags,

    })

# UC16 - Gerar Relatório de Vendas para Chefe
@login_required
def relatorio_vendas_chefe(request):
    try:
        chefe = E_Chefe.objects.get(usuario=request.user)
    except E_Chefe.DoesNotExist:
        messages.error(request, "Acesso negado. Apenas Chefes podem visualizar relatórios de vendas.")
        return redirect('home')

    TAXA_ADM = Decimal("0.10")
    
    relatorio = E_Receita.objects.filter(autor=chefe).annotate(
        
        total_vendas=Count('vendas'),
        
        receita_bruta_calculada=ExpressionWrapper(
            F('preco') * F('total_vendas'),
            output_field=DecimalField(decimal_places=2)
        ),

        taxa_deduzida=ExpressionWrapper(
            F('receita_bruta_calculada') * TAXA_ADM,
            output_field=DecimalField(decimal_places=2)
        ),
        
        receita_liquida=ExpressionWrapper(
            F('receita_bruta_calculada') - F('taxa_deduzida'),
            output_field=DecimalField(decimal_places=2)
        )
    ).order_by('-total_vendas')

    receitas_com_vendas = relatorio.exclude(total_vendas=0)
    
    total_vendas_geral = receitas_com_vendas.aggregate(Sum('total_vendas'))['total_vendas__sum'] or 0
    receita_bruta_geral = receitas_com_vendas.aggregate(Sum('receita_bruta_calculada'))['receita_bruta_calculada__sum'] or Decimal(0)
    receita_liquida_geral = receitas_com_vendas.aggregate(Sum('receita_liquida'))['receita_liquida__sum'] or Decimal(0)

    context = {
        'chefe': chefe,
        'relatorio': relatorio, 
        'total_vendas_geral': total_vendas_geral,
        'receita_bruta_geral': receita_bruta_geral,
        'receita_liquida_geral': receita_liquida_geral,
        'receitas_sem_vendas': relatorio.filter(total_vendas=0).count(),
    }

    return render(request, 'F_Tela_Relatorio_Vendas.html', context)


#UC17 - Editar/Excluir Receita
@login_required
def editar_receita(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)
    
    try:
        chefe_logado = E_Chefe.objects.get(usuario=request.user)
    except E_Chefe.DoesNotExist:
        messages.error(request, "Acesso negado. Você não é um Chefe.")
        return redirect('visualizar_receita', receita_id=receita_id)
    
    if receita.autor != chefe_logado:
        messages.error(request, "Acesso negado. Você não é o autor desta receita.")
        return redirect('visualizar_receita', receita_id=receita_id)

    if request.method == 'POST':
        receita.nome = request.POST.get('nome')
        receita.descricao = request.POST.get('descricao')
        receita.preco = request.POST.get('preco')
        receita.modo_de_preparo = request.POST.get('modo_de_preparo')
        tempo_preparo = request.POST.get('tempo_preparo')
        receita.dificuldade = request.POST.get('dificuldade')
        
        foto_nova = request.FILES.get('foto_receita')
        if foto_nova:
            receita.foto = foto_nova
        
        try:
            receita.tempo_preparo = int(tempo_preparo)
        except (ValueError, TypeError):
            pass

        receita.save()

        tags_selecionadas = request.POST.getlist('tags')
        receita.tags.clear()
        for nome_tag in tags_selecionadas:
            tag, _ = E_Tag.objects.get_or_create(nome=nome_tag)
            receita.tags.add(tag)

        ingredientes_texto = request.POST.get('ingredientes', '')
        ingredientes_lista = [i.strip() for i in ingredientes_texto.split(',') if i.strip()]
        receita.ingredientes.clear()
        for nome_ingrediente in ingredientes_lista:
            ingrediente, _ = E_Ingrediente.objects.get_or_create(nome=nome_ingrediente)
            receita.ingredientes.add(ingrediente)

        messages.success(request, f'Receita "{receita.nome}" atualizada com sucesso!')
        return redirect('visualizar_receita', receita_id=receita.id)

    ingredientes_string = ", ".join([i.nome for i in receita.ingredientes.all()])
    
    context = {
        'receita': receita,
        'tags': E_Receita.TAGS_PADRAO,
        'ingredientes_string': ingredientes_string,
    }
    
    return render(request, 'F_Tela_Cadastro_Receita.html', context)


#UC17 - Editar/Excluir Receita

@login_required
def chefe_excluir_receita(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)

    try:
        chefe_logado = E_Chefe.objects.get(usuario=request.user)
    except E_Chefe.DoesNotExist:
        messages.error(request, "Acesso negado. Você não é um Chefe.")
        return redirect('visualizar_receita', receita_id=receita_id)

    if receita.autor != chefe_logado:
        messages.error(request, "Acesso negado. Você não é o autor desta receita.")
        return redirect('visualizar_receita', receita_id=receita_id)

    if request.method == 'POST':
        nome_receita = receita.nome
        receita.delete()
        messages.success(request, f'A receita \"{nome_receita}\" foi excluída com sucesso.')
        return redirect('home')  

    return redirect('visualizar_receita', receita_id=receita_id)


@login_required
def adicionar_ao_carrinho(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)

    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem comprar.")
        return redirect("visualizar_receita", receita_id=receita_id)

    carrinho = request.session.get("carrinho", [])

    if receita_id not in carrinho:
        carrinho.append(receita_id)
        request.session["carrinho"] = carrinho
        messages.success(request, "Receita adicionada ao carrinho!")
    else:
        messages.info(request, "Esta receita já está no carrinho.")

    return redirect("ver_carrinho")

@login_required
def ver_carrinho(request):
    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem comprar.")
        return redirect("home")

    carrinho = request.session.get("carrinho", [])

    receitas = E_Receita.objects.filter(id__in=carrinho)
    total = sum(r.preco for r in receitas)

    return render(request, "F_Tela_Carrinho.html", {
        "receitas": receitas,
        "total": total
    })

@login_required
def remover_do_carrinho(request, receita_id):
    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem comprar.")
        return redirect("home")

    carrinho = request.session.get("carrinho", [])

    if receita_id in carrinho:
        carrinho.remove(receita_id)
        request.session["carrinho"] = carrinho
        messages.success(request, "Receita removida do carrinho.")
    else:
        messages.info(request, "Essa receita não estava no carrinho.")

    return redirect("ver_carrinho")


@login_required
def pagamento_carrinho(request):
    # Verifica se é consumidor
    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem comprar.")
        return redirect("home")

    # Carrinho armazenado na sessão
    carrinho = request.session.get("carrinho", [])

    if not carrinho:
        messages.info(request, "Seu carrinho está vazio.")
        return redirect("ver_carrinho")

    receitas = E_Receita.objects.filter(id__in=carrinho)
    total = sum(r.preco for r in receitas)

    if request.method == "POST":
        metodo = request.POST.get("tipo_pagamento")

        if metodo not in ["pix", "credito", "debito"]:
            messages.error(request, "Método de pagamento inválido.")
            return redirect("selecionar_pagamento_carrinho")

        taxa_adm = total * Decimal("0.10")

        # Criar pagamento
        pagamento = E_Pagamento.objects.create(
            consumidor=consumidor,
            tipo_pagamento=metodo,
            preco_total=total,
            taxa_adm=taxa_adm,
        )

        # Criar compras individuais
        for receita in receitas:
            E_Compra.objects.create(
                consumidor=consumidor,
                receita=receita,
                pagamento=pagamento
            )

        # Limpar carrinho
        request.session["carrinho"] = []

        messages.success(request, "Pagamento realizado com sucesso!")
        return redirect("home")

    return render(request, "F_Tela_Pagamento.html", {
        "receitas": receitas,
        "total": total
    })


@login_required
def minhas_receitas(request):
    try:
        consumidor = E_Consumidor.objects.get(usuario=request.user)
    except E_Consumidor.DoesNotExist:
        messages.error(request, "Somente consumidores podem acessar esta página.")
        return redirect("home")

    compras = E_Compra.objects.filter(consumidor=consumidor).select_related("receita")

    receitas = [compra.receita for compra in compras]

    return render(request, "F_Tela_Minhas_Receitas.html", {
        "receitas": receitas
    })



@login_required
@user_passes_test(lambda u: u.is_superuser)
def listar_usuarios(request):
    usuarios = E_UsuarioGeral.objects.all()
    return render(request, "F_Tela_ADM_Ver_Usuarios.html", {"usuarios": usuarios})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def bloquear_usuario(request, user_id):
    user = get_object_or_404(E_UsuarioGeral, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, "Usuário bloqueado com sucesso.")
    return redirect("listar_usuarios")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def desbloquear_usuario(request, user_id):
    user = get_object_or_404(E_UsuarioGeral, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, "Usuário desbloqueado com sucesso.")
    return redirect("listar_usuarios")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def listar_receitas(request):
    receitas = E_Receita.objects.all().select_related("autor")
    return render(request, "F_Tela_ADM_Ver_Receitas.html", {"receitas": receitas})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def adm_excluir_receita(request, receita_id):
    receita = get_object_or_404(E_Receita, id=receita_id)
    receita.delete()
    messages.success(request, "Receita excluída.")
    return redirect("listar_receitas")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(E_Avaliacoes, id=comentario_id)
    comentario.delete()
    messages.success(request, "Comentário removido.")
    return redirect("listar_comentarios")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def listar_comentarios(request):
    comentarios = E_Avaliacoes.objects.all().select_related("receita", "consumidor")
    return render(request, "F_Tela_ADM_Ver_Comentarios.html", {"comentarios": comentarios})

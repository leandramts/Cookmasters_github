# Cookmasters_app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import E_UsuarioGeral, E_Chefe, E_Consumidor, E_Receita, E_Ingrediente
from django.core.exceptions import ObjectDoesNotExist

# ----------------------------------------
# View da Home (Antigo app 'home')
# ----------------------------------------
def home_view(request):
    receitas_em_destaque = E_Receita.objects.order_by('-nota')[:6]
    contexto = {
        'receitas': receitas_em_destaque
    }
    return render(request, 'home.html', contexto)

# ----------------------------------------
# Views de Autenticação (Antigo 'usuarios')
# REESCRITAS SEM FORMS.PY
# ----------------------------------------

def login_view(request):
    """
    View de login manual, sem AuthenticationForm.
    """
    if request.method == 'POST':
        # 1. Obter dados brutos do HTML
        email = request.POST.get('email')
        senha = request.POST.get('password') # O <input> do HTML deve ter name="password"

        # 2. Validação básica
        if not email or not senha:
            messages.error(request, "Por favor, preencha o e-mail e a senha.")
            return render(request, 'F_Tela_Login.html')

        # 3. Autenticar o usuário
        # O Django vai procurar o E_UsuarioGeral porque você definiu AUTH_USER_MODEL
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            # 4. Sucesso: Logar e redirecionar
            login(request, user)
            return redirect('home')
        else:
            # 5. Falha: Mostrar erro
            messages.error(request, "E-mail ou senha inválidos.")
            return render(request, 'F_Tela_Login.html')
    else:
        # GET: Apenas mostrar a página de login
        return render(request, 'F_Tela_Login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# ----------------------------------------
# Views de Cadastro (Antigo 'usuarios')
# REESCRITAS SEM FORMS.PY
# ----------------------------------------

def escolher_tipo_usuario(request):
    """Apenas mostra a página de escolha."""
    return render(request, 'F_Tela_Escolher_Tipo.html')

def cadastro_consumidor(request):
    """
    View de cadastro manual de Consumidor, sem ModelForm.
    """
    if request.method == 'POST':
        # 1. Obter todos os dados brutos do HTML
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')

        # 2. Validação Manual de Dados
        if not nome or not email or not senha or not senha_confirm:
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

        if senha != senha_confirm:
            messages.error(request, "As senhas não são iguais.")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')
        
        # (Validação de força da senha deveria ir aqui)

        if E_UsuarioGeral.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

        # 3. Salvar no Banco de Dados (Manual)
        try:
            # Usamos create_user para garantir que a senha seja HASHED (criptografada)
            user = E_UsuarioGeral.objects.create_user(
                email=email,
                nome=nome,
                password=senha
            )
            # Criar o perfil de consumidor associado
            E_Consumidor.objects.create(usuario=user)

            # 4. Sucesso: Logar e redirecionar
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Consumidor {nome} cadastrado com sucesso!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao criar sua conta: {e}")
            return render(request, 'F_Tela_Cadastro_Consumidor.html')

    else:
        # GET: Apenas mostrar a página de cadastro
        return render(request, 'F_Tela_Cadastro_Consumidor.html')

def cadastro_chefe(request):
    """
    View de cadastro manual de Chefe.
    """
    if request.method == 'POST':
        # 1. Obter dados
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_confirm = request.POST.get('senha_confirm')
        cpf = request.POST.get('cpf')
        # ... (obter outros campos: dados_bancarios, etc.) ...

        # 2. Validação (FAZER IGUAL AO cadastro_consumidor)
        # (Verificar senhas, se email existe, etc.)
        if senha != senha_confirm:
            messages.error(request, "As senhas não são iguais.")
            return render(request, 'F_Tela_Cadastro_Chefe.html')
        
        if not cpf: # Exemplo de validação extra
             messages.error(request, "O CPF é obrigatório para Chefes.")
             return render(request, 'F_Tela_Cadastro_Chefe.html')

        # 3. Salvar (Manual)
        try:
            user = E_UsuarioGeral.objects.create_user(
                email=email,
                nome=nome,
                password=senha
            )
            # Criar o perfil de Chefe com os dados extras
            E_Chefe.objects.create(
                usuario=user, 
                cpf=cpf
                # ... (outros campos: dados_bancarios=dados_bancarios, etc.) ...
            )

            # 4. Sucesso
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Chefe {nome} cadastrado com sucesso!')
            return redirect('historia_chefe') # Redireciona SEM namespace

        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")
            return render(request, 'F_Tela_Cadastro_Chefe.html')

    else:
        # GET
        return render(request, 'F_Tela_Cadastro_Chefe.html')

def cadastro_adm(request):
    # Sua lógica de solicitação (por enquanto, tudo bem)
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.info(request, f'Solicitação de acesso enviada para ({email}).')
        return redirect('home')
    return render(request, 'F_Tela_Cadastro_Adm.html')


@login_required
def historia_chefe(request):
    """
    View manual para editar a descrição do Chefe.
    """
    try:
        chefe_perfil = request.user.e_chefe
    except ObjectDoesNotExist:
        messages.error(request, "Você não tem um perfil de Chefe.")
        return redirect('home')

    if request.method == 'POST':
        # 1. Obter dados
        descricao = request.POST.get('descricao')

        # 2. Salvar (Manual)
        chefe_perfil.descricao = descricao
        chefe_perfil.save()

        # 3. Sucesso
        messages.success(request, "Sua história foi atualizada!")
        return redirect('home')
    else:
        # GET: Mostrar página com dados existentes
        contexto = {'chefe': chefe_perfil}
        return render(request, 'F_Tela_Historia_Chefe.html', contexto)

# ----------------------------------------
# Views de Receitas (Antigo app 'receitas')
# ----------------------------------------

def cadastrar_receita(request):
    # Você terá que reescrever esta view também,
    # manualmente, como fizemos com o cadastro.
    # Por enquanto, vamos apenas renderizar o template.
    
    # Lógica de sessão (se você ainda a usa)
    ingredientes_ids = request.session.get('ingredientes_ids', [])
    ingredientes = E_Ingrediente.objects.filter(id__in=ingredientes_ids)
    contexto = {'ingredientes': ingredientes}
    
    return render(request, 'receita_form.html', contexto)

def cadastrar_ingredientes(request):
    # Esta view também precisa ser reescrita
    # para salvar o ingrediente manualmente.
    return render(request, 'ingredientes_form.html')
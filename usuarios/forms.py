# usuarios/forms.py
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from .models import E_UsuarioGeral
from django import forms
from django.contrib.auth.models import Group  
from .models import E_UsuarioGeral, E_Chefe, E_Consumidor

TIPO_USUARIO_CHOICES = (
    ('consumidor', 'Consumidor'),
    ('chefe', 'Chefe'),
    ('admin', 'Administrador'),
)

class FormularioCadastroUsuario(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    senha_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO_CHOICES,
        widget=forms.RadioSelect, 
        required=True,
        label=''
    )

    class Meta:
        model = E_UsuarioGeral
        fields = ('nome', 'email')
    
    def clean_senha_confirm(self):
        senha = self.cleaned_data.get('senha')
        senha_confirm = self.cleaned_data.get('senha_confirm')
        if senha and senha_confirm and senha != senha_confirm:
            raise forms.ValidationError("As senhas não são iguais.")
        return senha_confirm

    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']
        
        user.set_password(self.cleaned_data['senha'])
        
        user.is_staff = False
        user.is_superuser = False
        
        if commit:
            user.save()

        tipo = self.cleaned_data.get('tipo_usuario')
        
        if tipo == 'chefe':
            E_Chefe.objects.create(usuario=user)
        
        elif tipo == 'admin':
            try:
                admin_group = Group.objects.get(name='Administradores')
                user.groups.add(admin_group)
            except Group.DoesNotExist:
                print("AVISO DE SEGURANÇA: Grupo 'Administradores' não encontrado. Usuário criado como Consumidor.")
                E_Consumidor.objects.create(usuario=user)
        
        else:
            E_Consumidor.objects.create(usuario=user)
        
        return user
class FormularioCadastroChefe(forms.ModelForm):
    cpf = forms.CharField(max_length=14, label="CPF", required=True)
    dados_bancarios = forms.CharField(
        max_length=150, 
        label="Dados Bancários",
        widget=forms.TextInput(attrs={'placeholder': 'Banco, agência, conta...'})
    )
    descricao = forms.CharField(
        label="Descrição / História do Chefe",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Conte um pouco sobre sua trajetória culinária...'})
    )
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    senha_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")

    class Meta:
        model = E_UsuarioGeral
        fields = ('nome', 'email', 'cpf', 'dados_bancarios', 'descricao')

    def clean_senha_confirm(self):
        senha = self.cleaned_data.get('senha')
        senha_confirm = self.cleaned_data.get('senha_confirm')
        if senha and senha_confirm and senha != senha_confirm:
            raise forms.ValidationError("As senhas não são iguais.")
        return senha_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['senha'])
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()
            E_Chefe.objects.create(
                usuario=user,
                cpf=self.cleaned_data['cpf'],
                dados_bancarios=self.cleaned_data['dados_bancarios'],
                descricao=self.cleaned_data['descricao']
            )

        return user

class FormularioCadastroConsumidor(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    senha_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")

    class Meta:
        model = E_UsuarioGeral
        fields = ('nome', 'email')

    def clean_senha_confirm(self):
        senha = self.cleaned_data.get('senha')
        senha_confirm = self.cleaned_data.get('senha_confirm')
        if senha and senha_confirm and senha != senha_confirm:
            raise forms.ValidationError("As senhas não são iguais.")
        return senha_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['senha'])
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()
            E_Consumidor.objects.create(usuario=user)

        return user

class FormularioCadastroAdm(forms.ModelForm):
    email = forms.EmailField(label="E-mail corporativo")
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")
    codigo_empresa = forms.CharField(
        label="Código de Acesso da Empresa",
        max_length=30,
        required=True,
        help_text="Informe o código fornecido pela empresa para liberar o acesso."
    )

    class Meta:
        model = E_UsuarioGeral
        fields = ('email',)

    def clean_codigo_empresa(self):
        codigo = self.cleaned_data.get('codigo_empresa')
        if codigo != "LIBERA2025":  # Exemplo de liberaçaõ que a gnte pode fazer — depois pode ligar isso ao BD
            raise forms.ValidationError("Código de acesso inválido. Peça à empresa um novo código.")
        return codigo

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['senha'])
        user.is_staff = True
        user.is_superuser = False

        if commit:
            user.save()
            try:
                admin_group = Group.objects.get(name='Administradores')
                user.groups.add(admin_group)
            except Group.DoesNotExist:
                print(" Grupo 'Administradores' não encontrado.")
        return user


class FormularioLoginUsuario(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control'})
    )

    password = forms.CharField(
        label='Senha', 
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )
class HistoriaChefeForm(forms.Form):
    nome = forms.CharField(label='Nome do Chef', max_length=100)
    descricao = forms.CharField(label='Resumo da História', widget=forms.Textarea)
    receitas = forms.CharField(label='Principais Receitas', widget=forms.Textarea)


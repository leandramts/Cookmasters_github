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

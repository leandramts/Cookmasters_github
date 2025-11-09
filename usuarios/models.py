from django.db import models
from django.contrib.auth.models import AbstractUser

class E_UsuarioGeral(AbstractUser):
    #Herda email e senha de AbstractUser
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']


class E_Chefe(models.Model):
    usuario = models.OneToOneField(E_UsuarioGeral, on_delete=models.CASCADE)

    cpf = models.CharField(max_length=14, unique=True)
    numero_agencia = models.CharField(max_length=10)
    nome_do_banco = models.CharField(max_length=30)
    descricao = models.TextField(blank=True)
    Nota = models.FloatField(default=0.0)
    Numero_conta = models.CharField(max_length=50)

    def __str__(self):
        return self.usuario.email

class E_Consumidor(models.Model):
    usuario = models.OneToOneField(E_UsuarioGeral, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.email

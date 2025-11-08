from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class E_UsuarioGeral(AbstractUser):
    #Herda email e senha de AbstractUser
    nome = models.CharField(max_length=100)

class E_Chefe(models.Model):
    usuario = models.OneToOneField(E_UsuarioGeral, on_delete=models.CASCADE)

    cpf = models.CharField(max_length=14, unique=True)
    numero_agencia = models.IntegerField(max_length=6)
    nome_do_banco = models.CharField(max_length=30)
    descricao = models.CharField()
    Nota = models.FloatField(max_length=4)
    Numero_conta = models.CharField(max_length=50)

    def __str__(self):
        return self.usuario.nome

class E_Consumidor(models.Model):
    usuario = models.OneToOneField(E_UsuarioGeral, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.nome

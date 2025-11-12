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


class E_Ingrediente(models.Model):
    nome = models.CharField(max_length=100, unique=True)
     
    def __str__(self):
        return self.nome

class E_Receita(models.Model):
    TAGS = [
        ('LOW CARB', 'Low Carb'),
        ('SEM LACTOSE', 'Sem Lactose'),
        ('SEM GLUTEN', 'Sem Glúten'),
        ('VEGANO', 'Vegano'),
        ('VEGETARIANO', 'Vegetariano'),
        ('LOW FAT', 'Low Fat'),
        ('HIGH PROTEIN', 'High Protein'),
        ('SEM SOJA', 'Sem Soja'),
    ]
    autor = models.ForeignKey(E_Chefe, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    descricao = models.TextField()
    nota = models.IntegerField(default=0)
    tag = models.CharField(max_length=50, choices=TAGS, blank=True)

    def __str__(self):
        return self.nome


class E_Avaliacoes(models.Model):
    receita = models.ForeignKey(E_Receita, on_delete=models.CASCADE)
    consumidor = models.ForeignKey(E_UsuarioGeral, on_delete=models.CASCADE)
    nota = models.IntegerField() # Ex: de 1 a 5
    comentario = models.TextField(blank=True)

class E_Pagamento(models.Model):
    consumidor = models.ForeignKey(E_Consumidor, on_delete=models.SET_NULL, null=True)
    tipo_pagamento = models.CharField(max_length=50) 
    preco_total = models.DecimalField(max_digits=7, decimal_places=2)
    taxa_adm = models.DecimalField(max_digits=5, decimal_places=2)

    #Numero de cartao, nome do banco, senha estão num gateway de pagamento
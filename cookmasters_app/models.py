from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class E_UsuarioGeralManager(BaseUserManager):

    
    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo Email é obrigatório')
        if not nome:
            raise ValueError('O campo Nome é obrigatório')

        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(email, nome, password, **extra_fields)

class E_UsuarioGeral(AbstractUser):
    username = None
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    objects = E_UsuarioGeralManager()
    def __str__(self):
        return self.email


class E_Chefe(models.Model):
    usuario = models.OneToOneField(E_UsuarioGeral, on_delete=models.CASCADE)

    cpf = models.CharField(max_length=14, unique=True)
    numero_agencia = models.CharField(max_length=10, blank=True, null=True)
    nome_do_banco = models.CharField(max_length=30, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    Nota = models.FloatField(default=0.0)
    Numero_conta = models.CharField(max_length=50, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_chefes', blank=True, null=True)

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

class E_Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class E_Receita(models.Model):
    TAGS_PADRAO = [
        'Low Carb', 'Sem Lactose', 'Sem Glúten', 'Vegano',
        'Vegetariano', 'Low Fat', 'High Protein', 'Sem Soja',
    ]
    autor = models.ForeignKey(E_Chefe, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    descricao = models.TextField()
    modo_de_preparo = models.TextField(default="Sem modo de preparo informado")
    tempo_preparo = models.IntegerField(default=0)
    DIFICULDADE_CHOICES = [
            ('facil', 'Fácil'),
            ('medio', 'Médio'),
            ('dificil', 'Difícil'),
        ]

    dificuldade = models.CharField(
            max_length=10,
            choices=DIFICULDADE_CHOICES,
            default='facil'
        )

    nota = models.IntegerField(default=0)
    tags = models.ManyToManyField(E_Tag, related_name='receitas', blank=True)
    ingredientes = models.ManyToManyField('E_Ingrediente', related_name='receitas')
    foto = models.ImageField(upload_to='fotos_receitas', blank=True, null=True)

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

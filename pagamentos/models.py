from django.db import models
from usuarios.models import E_Consumidor

# Create your models here.
class E_Pagamento(models.Model):
    consumidor = models.ForeignKey(E_Consumidor, on_delete=models.SET_NULL, null=True)
    tipo_pagamento = models.CharField(max_length=50) 
    preco_total = models.DecimalField(max_digits=7, decimal_places=2)
    taxa_adm = models.DecimalField(max_digits=5, decimal_places=2)

    #Numero de cartao, nome do banco, senha estão num gateway de pagamento
    
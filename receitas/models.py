from django.db import models
from usuarios.models import E_Chefe
from usuarios.models import E_UsuarioGeral

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

    ingredientes = models.ManyToManyField(E_Ingrediente, through='ReceitaIngrediente')

    def __str__(self):
        return self.nome

#classe intermediaria (perguntar se precisa botar na documentacao)   
class ReceitaIngrediente(models.Model):
    receita = models.ForeignKey(E_Receita, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(E_Ingrediente, on_delete=models.CASCADE)
    quantidade = models.CharField(max_length=100)  

    class Meta:
        unique_together = ('receita', 'ingrediente')

class E_Avaliacoes(models.Model):
    receita = models.ForeignKey(E_Receita, on_delete=models.CASCADE)
    consumidor = models.ForeignKey(E_UsuarioGeral, on_delete=models.CASCADE)
    nota = models.IntegerField() # Ex: de 1 a 5
    comentario = models.TextField(blank=True)
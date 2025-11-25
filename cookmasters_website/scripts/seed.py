# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from decimal import Decimal
import random

from cookmasters_app.models import (
    E_Chefe, E_Consumidor, E_Receita,
    E_Tag, E_Ingrediente
)

User = get_user_model()

TAGS_DISPONIVEIS = E_Receita.TAGS_PADRAO

ingredientes_lista = ["Ovo", "Açúcar", "Farinha", "Leite", "Manteiga", "Sal", "Pimenta", "Cebola", "Tomate"]

RECEITAS_DETALHADAS = [
    {
        "nome": "Bolo Vegano de Laranja",
        "chef_idx": 0, "preco": 22.50, "tempo": 60, "dificuldade": "medio",
        "ingredientes": ["Açúcar", "Farinha", "Sal"],
        "tags": ["Vegano", "Sem Glúten", "Sem Lactose"]
    },
    {
        "nome": "Omelete High Protein",
        "chef_idx": 1, "preco": 10.90, "tempo": 15, "dificuldade": "facil",
        "ingredientes": ["Ovo", "Sal", "Pimenta"],
        "tags": ["Low Carb", "High Protein", "Sem Lactose"]
    },
    {
        "nome": "Frango Low Carb no Azeite",
        "chef_idx": 2, "preco": 40.00, "tempo": 25, "dificuldade": "facil",
        "ingredientes": ["Sal", "Pimenta", "Cebola"],
        "tags": ["Low Carb", "High Protein", "Low Fat"]
    },
    {
        "nome": "Pudim Sem Lactose",
        "chef_idx": 3, "preco": 18.00, "tempo": 120, "dificuldade": "dificil",
        "ingredientes": ["Açúcar", "Ovo", "Sal"],
        "tags": ["Sem Lactose", "Vegetariano"]
    },
    {
        "nome": "Sopa Detox (Sem Glúten e Soja)",
        "chef_idx": 4, "preco": 25.90, "tempo": 45, "dificuldade": "medio",
        "ingredientes": ["Cebola", "Tomate", "Sal"],
        "tags": ["Sem Glúten", "Sem Soja", "Vegetariano"]
    },
    {
        "nome": "Biscoito Sem Glúten e Low Fat",
        "chef_idx": 0, "preco": 12.00, "tempo": 30, "dificuldade": "facil",
        "ingredientes": ["Farinha", "Açúcar", "Manteiga"],
        "tags": ["Sem Glúten", "Low Fat", "Vegetariano"]
    },
    {
        "nome": "Massa Sem Soja e Vegana",
        "chef_idx": 1, "preco": 35.00, "tempo": 40, "dificuldade": "medio",
        "ingredientes": ["Tomate", "Sal", "Cebola"],
        "tags": ["Vegano", "Sem Soja", "Sem Glúten"]
    },
    {
        "nome": "Torta High Protein e Low Carb",
        "chef_idx": 2, "preco": 60.00, "tempo": 90, "dificuldade": "dificil",
        "ingredientes": ["Ovo", "Manteiga", "Farinha"],
        "tags": ["High Protein", "Low Carb", "Sem Lactose"]
    },
]

print("Limpando banco...")

E_Receita.objects.all().delete()
E_Chefe.objects.all().delete()
E_Consumidor.objects.all().delete()
E_Tag.objects.all().delete()
E_Ingrediente.objects.all().delete()
User.objects.all().delete()

print("Criando tags a partir de E_Receita.TAGS_PADRAO...")
tags_objetos = {t.nome: t for t in [E_Tag.objects.create(nome=t) for t in TAGS_DISPONIVEIS]}

print("Criando usuários, chefes e consumidores...")

chef_users = []
for i in range(5):
    user = User.objects.create_user(
        email=f"chef{i}@exemplo.com",
        nome=f"Chef {i}",
        password="123456"
    )
    chef_users.append(user)

# Caminho da foto padrão do Chefe
foto_chefe_padrao = "fotos_chefes/gatinho.jpg"

chefs = []
for i, u in enumerate(chef_users):
    chef = E_Chefe.objects.create(
        usuario=u,
        cpf=f"000.000.000-0{i}",
        descricao=f"Chef especialista em dietas {['Low Carb', 'Veganas', 'Fitness'][i % 3]}",
        foto=foto_chefe_padrao # Foto padrão para o Chefe
    )
    chefs.append(chef)

for i in range(10):
    user = User.objects.create_user(
        email=f"user{i}@exemplo.com",
        nome=f"Cliente {i}",
        password="123456"
    )
    E_Consumidor.objects.create(usuario=user)

print("Criando ingredientes...")

ingredientes_objetos = {i.nome: i for i in [E_Ingrediente.objects.create(nome=i) for i in ingredientes_lista]}


print("Criando receitas coerentes...")

foto_receita_padrao = "fotos_receitas/default.jpg"

for i, dados in enumerate(RECEITAS_DETALHADAS):
    chef = chefs[dados["chef_idx"]]
    
    dificuldade_str = dados["dificuldade"] 
    
    nota_inicial = Decimal(str(round(random.uniform(3.0, 5.0), 1)))

    receita = E_Receita.objects.create(
        autor=chef,
        nome=dados["nome"],
        preco=Decimal(str(dados["preco"])),
        descricao=f'{dados["nome"]}, uma receita {dificuldade_str} de preparo.',
        tempo_preparo=dados["tempo"],
        dificuldade=dificuldade_str,
        modo_de_preparo=f"Misture os ingredientes e asse/cozinhe por aproximadamente {dados['tempo']} minutos.",
        foto=foto_receita_padrao,
        nota=nota_inicial
    )

    for tag_nome in dados["tags"]:
        tag = tags_objetos.get(tag_nome)
        if tag:
            receita.tags.add(tag)

    for ing_nome in dados["ingredientes"]:
        ing = ingredientes_objetos.get(ing_nome)
        if ing:
            receita.ingredientes.add(ing)

    if i < 5:
        from cookmasters_app.models import E_Avaliacoes
        from cookmasters_app.models import E_Compra
        
        consumidor_teste = E_Consumidor.objects.get(usuario__email='user0@exemplo.com')
        
        if not E_Compra.objects.filter(consumidor=consumidor_teste, receita=receita).exists():
            E_Compra.objects.create(consumidor=consumidor_teste, receita=receita)
        
        E_Avaliacoes.objects.create(
            receita=receita,
            consumidor=consumidor_teste,
            nota=nota_inicial,
            comentario=f"Ótima receita {tag_nome.lower()}!"
        )
        
        receita.nota = nota_inicial
        receita.save()

print("\nFinalizado. Dados de teste criados com sucesso.")
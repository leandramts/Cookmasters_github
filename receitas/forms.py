from django import forms
from .models import E_Receita, E_Ingrediente

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = E_Ingrediente
        fields = ['nome']

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = E_Receita
        fields = ['autor', 'nome', 'preco', 'descricao', 'nota', 'tag', 'ingredientes']
        widgets = {
            'ingredientes': forms.CheckboxSelectMultiple(),  # permite selecionar múltiplos ingredientes
        }
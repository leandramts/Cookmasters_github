from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    E_UsuarioGeral, E_Chefe, E_Consumidor, 
    E_Ingrediente, E_Tag, E_Receita, E_Avaliacoes, E_Pagamento
)

class E_UsuarioGeralAdmin(UserAdmin):
    model = E_UsuarioGeral
    list_display = ['email', 'nome', 'is_staff', 'is_active']
    search_fields = ['email', 'nome']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password', 'password2'),
        }),
    )

admin.site.register(E_UsuarioGeral, E_UsuarioGeralAdmin)
admin.site.register(E_Chefe)
admin.site.register(E_Consumidor)
admin.site.register(E_Ingrediente)
admin.site.register(E_Tag)
admin.site.register(E_Receita)
admin.site.register(E_Avaliacoes)
admin.site.register(E_Pagamento)
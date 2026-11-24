from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "nome_completo", "tipo", "cidade", "moedas", "is_active")
    list_filter = ("tipo", "is_active", "is_staff")
    search_fields = ("email", "nome_completo", "cpf")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados pessoais", {"fields": ("nome_completo", "cpf", "telefone", "cidade")}),
        ("Perfil", {"fields": ("tipo", "sobre", "area_atuacao", "anos_experiencia", "moedas")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "nome_completo", "cpf", "telefone", "tipo", "password1", "password2")}),
    )

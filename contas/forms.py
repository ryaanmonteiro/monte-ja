from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import Usuario
from .validators import somente_digitos, validar_cpf


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"autofocus": True, "placeholder": "seu@email.com"}))
    password = forms.CharField(label="Senha", strip=False, widget=forms.PasswordInput(attrs={"placeholder": "Senha"}))


class CadastroForm(forms.ModelForm):
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput, help_text="Mínimo de 8 caracteres.")
    tipo = forms.ChoiceField(label="Quero me cadastrar como", choices=Usuario.TIPOS, widget=forms.RadioSelect, initial=Usuario.CLIENTE)

    class Meta:
        model = Usuario
        fields = ["nome_completo", "cpf", "telefone", "email", "senha", "tipo", "cidade"]

    def clean_cpf(self):
        cpf = somente_digitos(self.cleaned_data["cpf"])
        validar_cpf(cpf)
        if Usuario.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Já existe uma conta com este CPF.")
        return cpf

    def clean_telefone(self):
        telefone = somente_digitos(self.cleaned_data["telefone"])
        if len(telefone) not in (10, 11):
            raise forms.ValidationError("Informe o telefone com DDD (10 ou 11 dígitos).")
        return telefone

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email

    def clean_senha(self):
        senha = self.cleaned_data["senha"]
        validate_password(senha)
        return senha

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nome_completo", "telefone", "cidade", "sobre", "area_atuacao", "anos_experiencia"]
        widgets = {"sobre": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos de perfil profissional só fazem sentido para montadores.
        if not (self.instance and self.instance.eh_montador):
            for campo in ("sobre", "area_atuacao", "anos_experiencia"):
                del self.fields[campo]

    def clean_telefone(self):
        telefone = somente_digitos(self.cleaned_data["telefone"])
        if len(telefone) not in (10, 11):
            raise forms.ValidationError("Informe o telefone com DDD (10 ou 11 dígitos).")
        return telefone

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "contas"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="contas/login.html", authentication_form=LoginForm, redirect_authenticated_user=True), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("montador/<int:pk>/", views.perfil_montador, name="perfil_montador"),
    path("moedas/comprar/", views.comprar_moedas, name="comprar_moedas"),
]

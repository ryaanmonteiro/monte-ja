from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from servicos import views as servicos_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", servicos_views.home, name="home"),
    path("contas/", include("contas.urls")),
    path("", include("servicos.urls")),
    # Recuperação de senha (link "Esqueceu a senha?")
    path("senha/recuperar/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("senha/recuperar/enviado/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("senha/redefinir/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("senha/redefinir/concluido/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CadastroForm, PerfilForm
from .models import Usuario


def cadastro(request):
    """Tela 3 – Cadastro (Criar Conta)."""
    if request.user.is_authenticated:
        return redirect("home")
    form = CadastroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save(commit=False)
        if usuario.eh_montador:
            usuario.moedas = settings.MOEDAS_BONUS_CADASTRO
        usuario.save()
        login(request, usuario)
        messages.success(request, "Conta criada com sucesso! Bem-vindo(a) ao Monte Já.")
        return redirect("contas:editar_perfil" if usuario.eh_montador else "home")
    return render(request, "contas/cadastro.html", {"form": form})


def perfil_montador(request, pk):
    """Tela 4 – Perfil do Montador (contratação)."""
    montador = get_object_or_404(Usuario, pk=pk, tipo=Usuario.MONTADOR)
    context = {
        "montador": montador,
        "servicos": montador.servicos.filter(ativo=True),
        "ultimas_avaliacoes": montador.avaliacoes_recebidas.select_related("cliente")[:3],
    }
    return render(request, "contas/perfil_montador.html", context)


@login_required
def editar_perfil(request):
    form = PerfilForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil atualizado.")
        return redirect("contas:editar_perfil")
    return render(request, "contas/editar_perfil.html", {"form": form})


@login_required
@require_POST
def comprar_moedas(request):
    """Compra SIMULADA de moedas (não há pagamento real nesta versão acadêmica)."""
    if not request.user.eh_montador:
        messages.error(request, "Somente montadores usam moedas.")
        return redirect("home")
    Usuario.objects.filter(pk=request.user.pk).update(moedas=F("moedas") + settings.MOEDAS_PACOTE_SIMULADO)
    messages.success(request, f"{settings.MOEDAS_PACOTE_SIMULADO} moedas adicionadas (compra simulada).")
    proximo = request.POST.get("next", "")
    if proximo and url_has_allowed_host_and_scheme(proximo, allowed_hosts={request.get_host()}):
        return redirect(proximo)
    return redirect("servicos:disponiveis")
